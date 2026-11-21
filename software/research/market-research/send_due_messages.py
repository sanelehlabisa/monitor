"""Check saved CSV send dates; local tests only until real delivery is approved."""

import argparse
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from email.message import EmailMessage
from email.policy import SMTP as SMTP_POLICY
import hashlib
import json
import os
from pathlib import Path
import smtplib
import re
import ssl
from typing import Any, Callable

import phonenumbers

from pipeline import (CONTACT_FIELDS, WORKSPACE, RegisterError, atomic_write, csv_bytes, guarded_write,
                      load_contacts, normalize_email, normalize_phone, single_writer, workspace_path)


UTC = timezone.utc
LOCAL = timezone(timedelta(hours=2), "Africa/Johannesburg")
CHANNELS = ("email", "sms")
STATUSES = {"new", "scheduled", "sending", "sent", "failed", "skipped"}
DAILY_CAP, MAX_ATTEMPTS = 6, 3
Row = dict[str, str]


def load_templates(folder: Path | None = None) -> tuple[str, str, str]:
    folder = folder or WORKSPACE / "templates"
    values: dict[str, str] = {}
    for name in ("email.txt", "sms.txt"):
        path = folder / name
        if path.resolve().parent != folder.resolve():
            raise ValueError("Template paths must stay inside their template directory.")
        try:
            with path.open("rb") as source:
                content = source.read(32769)
            if len(content) > 32768:
                raise ValueError("Message templates must be at most 32 KiB each.")
            values[name] = content.decode("utf-8-sig").replace("\r\n", "\n").rstrip("\n")
        except (OSError, UnicodeError):
            raise ValueError("Both editable UTF-8 templates must exist under templates/.") from None
    header, separator, body = values["email.txt"].partition("\n\n")
    subject = header.removeprefix("Subject:").strip()
    if not header.startswith("Subject:") or not separator or not subject or any(ord(c) < 32 for c in subject):
        raise ValueError("email.txt needs a Subject: line, a blank line, then the email body.")
    sms = values["sms.txt"]
    if not body.strip() or not sms.strip() or "\x00" in body + sms:
        raise ValueError("Email/SMS message text must be nonempty plain text.")
    return subject, body, sms


def timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("An aware timestamp is required.")
    return value.astimezone(UTC).isoformat(timespec="seconds")


def parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        timestamp(parsed)
        return parsed.astimezone(UTC)
    except ValueError:
        raise RegisterError("Invalid or timezone-free delivery timestamp; CSV preserved.") from None


def local_day(value: str) -> date | None:
    parsed = parse_timestamp(value)
    return parsed.astimezone(LOCAL).date() if parsed else None


def working(now: datetime) -> bool:
    local = now.astimezone(LOCAL)
    return (local.weekday() < 5
            and time(9, 30) <= local.time().replace(second=0, microsecond=0, tzinfo=None) <= time(15, 30))


def validate_rows(rows: list[Row]) -> None:
    ids: set[int] = set()
    pairs: set[tuple[str, str]] = set()
    for row in rows:
        try:
            identity = int(row["id"])
            kind, value = row["contact_type"], row["contact_value"]
            pair = (kind, value)
            normalized = normalize_email(value) if kind == "email" else normalize_phone(value, True)[0]
            if identity < 1 or identity in ids or pair in pairs or kind not in {"email", "phone"} or not normalized or value != normalized:
                raise ValueError
            if row["email"] != (value if kind == "email" else "") or row["phone"] != (value if kind == "phone" else ""):
                raise ValueError
            ids.add(identity)
            pairs.add(pair)
            for channel in CHANNELS:
                if row[f"{channel}_status"] not in STATUSES or int(row[f"{channel}_attempts"]) < 0:
                    raise ValueError
                for suffix in ("scheduled_at", "sent_at", "last_attempt_at"):
                    parse_timestamp(row[f"{channel}_{suffix}"])
                if row[f"{channel}_status"] == "sent" and not row[f"{channel}_sent_at"]:
                    raise ValueError
                if row[f"{channel}_status"] == "sending" and (not row[f"{channel}_last_attempt_at"] or not int(row[f"{channel}_attempts"])):
                    raise ValueError
        except (ValueError, KeyError):
            raise RegisterError("Invalid contact/delivery state; CSV preserved for review.") from None


class ContactFile:
    """Caller holds the existing shared contacts lock for the complete transaction."""

    def __init__(self, path: Path) -> None:
        self.path = workspace_path(str(path))
        if not self.path.is_file():
            raise RegisterError("Contact CSV does not exist.")
        self.rows, self.original = load_contacts(self.path)
        validate_rows(self.rows)

    def check_unchanged(self) -> None:
        if self.path.read_bytes() != self.original:
            raise RegisterError("CSV changed outside this run; stop and review.")

    def save(self) -> None:
        validate_rows(self.rows)
        self.original = guarded_write(self.path, csv_bytes(CONTACT_FIELDS, self.rows), self.original)


def group_rows(row: Row, rows: list[Row]) -> list[Row]:
    group = row["contact_group"].strip()
    return [candidate for candidate in rows if candidate["contact_group"].strip() == group] if group else [row]


def held_reason(row: Row, channel: str, rows: list[Row]) -> str:
    kind = "email" if channel == "email" else "phone"
    if row["contact_type"] != kind:
        return "other_channel"
    if channel == "email":
        domain = row["email"].rsplit("@", 1)[-1]
        if domain == "ac.za" or domain.endswith(".ac.za"):
            return "academic_email"
    peers = group_rows(row, rows)
    if any(peer["contacted"].lower() == "true" or peer["response_status"].strip()
           or peer["status"].lower() in {"sent", "suppressed", "skipped", "do_not_contact", "opted_out"}
           or any(peer[f"{other}_status"] in {"sent", "sending"} for other in CHANNELS) for peer in peers):
        return "contacted_replied_or_unresolved"
    if channel == "sms":
        if not row["contact_group"].strip():
            return "unconfirmed_phone_only"
        if any(peer["contact_type"] == "email" for peer in peers):
            return "email_has_priority"
        number = phonenumbers.parse(row["phone"], "ZA")
        if not phonenumbers.is_valid_number(number) or phonenumbers.number_type(number) not in {
                phonenumbers.PhoneNumberType.MOBILE, phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE}:
            return "unconfirmed_sms_capability"
    return ""








class DeliveryError(Exception):
    def __init__(self, message: str, kind: str = "permanent") -> None:
        super().__init__(message)
        self.kind = kind


def append_log(path: Path, event: dict[str, object]) -> None:
    path = workspace_path(str(path))
    with path.open("a", encoding="utf-8") as output:
        output.write(json.dumps(event, ensure_ascii=False) + "\n")
        output.flush()
        os.fsync(output.fileno())


def send_sms(phone_number: str, message: str, *, capture: Path | None = None,
             outcome: str = "success") -> str:
    """Offline mock boundary only. Gateway environment values cannot enable HTTP."""
    if outcome not in {"success", "temporary", "permanent", "uncertain"}:
        raise ValueError("Unknown mock outcome.")
    if outcome != "success":
        raise DeliveryError("Local SMS mock: " + outcome, outcome)
    receipt = "mock-" + hashlib.sha256((phone_number + message).encode()).hexdigest()[:20]
    if capture is not None:
        append_log(capture, {"mode": "offline_mock", "receipt": receipt, "phone": phone_number, "message": message})
    return receipt


def send_email_local(recipient: str, sender: str, identity: str, port: int,
                     *, template: tuple[str, str] | None = None) -> str:
    if not normalize_email(sender) or normalize_email(recipient) != recipient or not recipient.endswith(".invalid") or not 1 <= port <= 65535:
        raise ValueError("Only validated fictional recipients and local SMTP ports are allowed.")
    subject, body = template or load_templates()[:2]
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = sender, recipient, subject
    digest = hashlib.sha256((identity + recipient + subject + body).encode()).hexdigest()[:24]
    receipt = f"<research-{digest}@{sender.rsplit('@', 1)[1]}>"
    message["Message-ID"] = receipt
    message.set_content(body)
    client = smtplib.SMTP(timeout=10)
    stage = "connect"
    try:
        client.connect("127.0.0.1", port)
        client.ehlo_or_helo_if_needed()
        for command, value in ((client.mail, sender), (client.rcpt, recipient)):
            code, _ = command(value)
            if not 200 <= code < 300:
                raise DeliveryError(f"SMTP envelope rejected ({code})", "temporary" if 400 <= code < 500 else "permanent")
        stage = "data"
        code, _ = client.data(message.as_bytes(policy=SMTP_POLICY))
        if code != 250:
            raise DeliveryError(f"SMTP DATA rejected ({code})", "temporary" if 400 <= code < 500 else "permanent")
        return receipt
    except smtplib.SMTPResponseException as error:
        code = error.smtp_code
        raise DeliveryError(f"SMTP rejected ({code})", "temporary" if 400 <= code < 500 else "permanent") from None
    except (OSError, smtplib.SMTPException):
        raise DeliveryError("Local SMTP connection interrupted", "uncertain" if stage == "data" else "temporary") from None
    finally:
        # A failed QUIT must never turn confirmed DATA acceptance into a resend.
        try:
            client.quit()
        except (OSError, smtplib.SMTPException):
            pass
        client.close()


def require_test_csv(path: Path, rows: list[Row]) -> None:
    test_root = workspace_path("data/local-test")
    canonical = workspace_path("data/contacts.csv")
    if not path.is_relative_to(test_root) or (canonical.exists() and path.samefile(canonical)):
        raise RegisterError("Delivery is test-only; use a synthetic CSV under data/local-test/.")
    for row in rows:
        if row["source_domain"] != "example.invalid" or (row["email"] and not row["email"].endswith(".invalid")):
            raise RegisterError("Local delivery requires fictional example.invalid fixture provenance.")


def due(row: Row, channel: str, rows: list[Row], now: datetime) -> bool:
    scheduled = parse_timestamp(row[f"{channel}_scheduled_at"])
    return (working(now) and row[f"{channel}_status"] in {"new", "scheduled"} and scheduled is not None
            and scheduled <= now
            and int(row[f"{channel}_attempts"]) < MAX_ATTEMPTS
            and local_day(row[f"{channel}_last_attempt_at"]) != now.astimezone(LOCAL).date()
            and not held_reason(row, channel, rows))


def day_usage(rows: list[Row], channel: str, now: datetime) -> int:
    today = now.astimezone(LOCAL).date()
    return sum(local_day(row[f"{channel}_last_attempt_at"]) == today
               or local_day(row[f"{channel}_sent_at"]) == today for row in rows)


def counters(rows: list[Row], now: datetime, sent_run: Counter[str] | None = None,
             failed_run: Counter[str] | None = None) -> dict[str, int]:
    sent_run = sent_run or Counter()
    if failed_run is None:
        failed_run = Counter({channel: sum(row[f"{channel}_status"] == "failed" for row in rows) for channel in CHANNELS})
    result: dict[str, int] = {}
    today = now.astimezone(LOCAL).date()
    for channel, plural in (("email", "Emails"), ("sms", "SMS")):
        result[f"{plural} sent today"] = sum(row[f"{channel}_status"] == "sent"
                                               and local_day(row[f"{channel}_sent_at"]) == today for row in rows)
        result[f"{plural} sent this run"] = sent_run[channel]
        result[f"{'Email' if channel == 'email' else 'SMS'} failures"] = failed_run[channel]
        result[f"Remaining {'email' if channel == 'email' else 'SMS'} contacts"] = sum(
            row[f"{channel}_status"] in {"new", "scheduled"} and not held_reason(row, channel, rows) for row in rows)
    result["Unconfirmed phone contacts"] = sum(row["contact_type"] == "phone" and not row["contact_group"].strip() for row in rows)
    result["Manual-review sending states"] = sum(row[f"{channel}_status"] == "sending" for row in rows for channel in CHANNELS)
    return result


def print_counters(result: dict[str, int], mode: str) -> None:
    print("Mode: " + mode)
    for label in ("Emails sent today", "SMS sent today", "Emails sent this run", "SMS sent this run",
                  "Email failures", "SMS failures", "Remaining email contacts", "Remaining SMS contacts",
                  "Unconfirmed phone contacts", "Manual-review sending states"):
        print(f"{label}: {result[label]}")


def run_local(path: Path, *, port: int = 1026, sender: str = "research@example.invalid",
              clock: Callable[[], datetime] | None = None, channels: tuple[str, ...] = CHANNELS) -> dict[str, int]:
    if not normalize_email(sender) or not 1 <= port <= 65535 or not channels or any(channel not in CHANNELS for channel in channels):
        raise ValueError("Invalid local delivery configuration.")
    clock = clock or (lambda: datetime.now(UTC))
    path = workspace_path(str(path))
    sent_run: Counter[str] = Counter()
    failed_run: Counter[str] = Counter()
    with single_writer(workspace_path("data/contacts.lock")):
        store = ContactFile(path)
        require_test_csv(path, store.rows)
        now = clock()
        if not working(now):
            result = counters(store.rows, now)
            print("Nothing due outside working hours or on weekends.")
            print_counters(result, "LOCAL TEST / SMS MOCK ONLY")
            return result
        subject, email_body, sms_body = load_templates()
        for channel in channels:
            if channel not in CHANNELS:
                raise ValueError("Unknown channel.")
            ordered = due_candidates(store.rows, channel, clock())
            for row in ordered:
                now = clock()
                if not working(now) or day_usage(store.rows, channel, now) >= DAILY_CAP:
                    break
                if not due(row, channel, store.rows, now):
                    continue
                store.check_unchanged()
                row[f"{channel}_status"] = "sending"
                row[f"{channel}_attempts"] = str(int(row[f"{channel}_attempts"]) + 1)
                row[f"{channel}_last_attempt_at"] = timestamp(now)
                row[f"{channel}_last_error"] = "Submission in progress; if interrupted, review manually before resetting."
                store.save()
                event: dict[str, object] = {"id": row["id"], "channel": channel, "at": timestamp(now), "state": "sending"}
                append_log(path.parent / "attempts.jsonl", event)
                try:
                    receipt = (send_email_local(row["email"], sender, row["id"], port, template=(subject, email_body)) if channel == "email"
                               else send_sms(row["phone"], sms_body, capture=path.parent / "sms-capture.jsonl"))
                except DeliveryError as error:
                    row[f"{channel}_last_error"] = str(error)[:300]
                    if error.kind == "uncertain":
                        row[f"{channel}_last_error"] = "Delivery uncertain; manual review required. " + str(error)[:200]
                    elif error.kind == "temporary" and int(row[f"{channel}_attempts"]) < MAX_ATTEMPTS:
                        row[f"{channel}_status"] = "scheduled"
                    else:
                        row[f"{channel}_status"] = "failed"
                    failed_run[channel] += 1
                    event.update(state=row[f"{channel}_status"], error_kind=error.kind)
                else:
                    row[f"{channel}_status"] = "sent"
                    row[f"{channel}_sent_at"] = timestamp(clock())
                    row[f"{channel}_last_error"] = ""
                    row["contacted"] = "true"
                    row["contacted_at"] = row[f"{channel}_sent_at"]
                    row["status"] = "sent"
                    sent_run[channel] += 1
                    event.update(state="sent", receipt=receipt)
                store.save()
                append_log(path.parent / "attempts.jsonl", event)
        result = counters(store.rows, clock(), sent_run, failed_run)
        print_counters(result, "LOCAL TEST / SMS MOCK ONLY")
        return result


def txt_records(name: str) -> dict[str, object]:
    import dns.exception
    import dns.resolver
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout, resolver.lifetime = 3, 6
        answer = resolver.resolve(name, "TXT")
        return {"status": "published", "records": [b"".join(record.strings).decode("utf-8", errors="replace") for record in answer]}
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return {"status": "absent", "records": []}
    except (dns.exception.DNSException, OSError) as error:
        return {"status": "unverified", "reason": type(error).__name__, "records": []}


def inspect_dns(domain: str, selector: str) -> dict[str, object]:
    result: dict[str, object] = {}
    for label, name, prefix in (("spf", domain, "v=spf1"), ("dmarc", "_dmarc." + domain, "v=DMARC1")):
        lookup = txt_records(name)
        selected = [record for record in lookup["records"] if record.startswith(prefix)]
        if lookup["status"] == "published" and len(selected) != 1:
            lookup.update(status="missing_or_multiple_policy_records")
        lookup["policy_records"] = selected
        result[label] = lookup
    result["dkim"] = txt_records(selector + "._domainkey." + domain) if selector else {
        "status": "unverified", "reason": "No confirmed selector supplied; actual signing also requires message evidence."}
    return result


def inspect_tls(host: str, port: int, implicit: bool) -> dict[str, object]:
    context = ssl.create_default_context()
    client: smtplib.SMTP | None = None
    try:
        client = (smtplib.SMTP_SSL(host, port, timeout=8, context=context) if implicit
                  else smtplib.SMTP(host, port, timeout=8))
        client.ehlo()
        if not implicit:
            if not client.has_extn("starttls"):
                return {"status": "blocked", "reason": "STARTTLS is not advertised; no downgrade/authentication attempted."}
            client.starttls(context=context)
            client.ehlo()
        return {"status": "tls_verified", "mode": "implicit_tls" if implicit else "required_starttls",
                "protocol": client.sock.version(), "authenticated": False, "mail_submitted": False}
    except (OSError, smtplib.SMTPException) as error:
        return {"status": "unverified", "reason": type(error).__name__, "authenticated": False, "mail_submitted": False}
    finally:
        if client is not None:
            client.close()


def readiness_blockers(report: dict[str, Any]) -> list[str]:
    result = ["Research-sender permission is unverified; confirm the configured SMTP account may send as this address.",
              "DKIM selector/signing is unverified; obtain provider setup evidence before production."]
    if not report.get("credentials_present"):
        result.append("Independent research SMTP username/password are missing or incomplete.")
    if report["tls"]["status"] != "tls_verified":
        result.append("SMTP TLS verification must pass without a downgrade.")
    for label in ("spf", "dmarc"):
        status = report["dns"][label]["status"]
        if status != "published":
            result.append(f"{label.upper()} policy needs review: {status}.")
    return result


def check_setup() -> int:
    from dotenv import dotenv_values
    values = dotenv_values(WORKSPACE / ".env", interpolate=False)
    required = ("RESEARCH_EMAIL_FROM", "SMTP_HOST", "SMTP_PORT", "SMTP_SECURE")
    if any(not values.get(key) for key in required):
        raise ValueError("Missing explicit sender/SMTP settings in market-research/.env; no app fallback or secrets printed.")
    sender = normalize_email(values["RESEARCH_EMAIL_FROM"] or "")
    port = int(values["SMTP_PORT"] or "0")
    secure = (values["SMTP_SECURE"] or "").lower()
    selector = values.get("RESEARCH_DKIM_SELECTOR", "") or ""
    if not sender or not 1 <= port <= 65535 or secure not in {"true", "false"}:
        raise ValueError("Invalid sender, SMTP port or SMTP_SECURE flag.")
    if selector and not re.fullmatch(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", selector):
        raise ValueError("Invalid DKIM selector.")
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "sender": sender,
              "config_source": "software/research/market-research/.env",
              "smtp_host": values["SMTP_HOST"], "smtp_port": port,
              "credentials_present": bool(values.get("SMTP_USER") and values.get("SMTP_PASSWORD")),
              "sender_authorization": "unverified; no authentication or production test message permitted",
              "tls": inspect_tls(values["SMTP_HOST"] or "", port, secure == "true"),
              "dns": inspect_dns(sender.rsplit("@", 1)[1], selector),
              "production_enabled": False,
              "notes": ["Published policies are not proof of alignment, valid authorization or actual DKIM signing.",
                        "Review all unverified/missing policies and sender permission before production approval."]}
    report["blockers"] = readiness_blockers(report)
    target = workspace_path("data/email-readiness.json")
    atomic_write(target, json.dumps(report, indent=2).encode())
    print("Read-only readiness report: data/email-readiness.json")
    print("TLS: " + report["tls"]["status"])
    for label, result in report["dns"].items():
        print(label.upper() + ": " + result["status"])
    print("Sender authorization/actual signing unverified; production remains disabled. No mail submitted.")
    return 0


def due_candidates(rows: list[Row], channel: str, now: datetime) -> list[Row]:
    remaining = max(0, DAILY_CAP - day_usage(rows, channel, now))
    ordered = sorted(rows, key=lambda row: (
        parse_timestamp(row[f"{channel}_scheduled_at"]) or datetime.max.replace(tzinfo=UTC), int(row["id"])))
    selected: list[Row] = []
    groups: set[str] = set()
    for row in ordered:
        if len(selected) >= remaining:
            break
        group = row["contact_group"].strip()
        if due(row, channel, rows, now) and (not group or group not in groups):
            selected.append(row)
            if group:
                groups.add(group)
    return selected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--report", action="store_true", help="read-only totals")
    mode.add_argument("--local-test", action="store_true", help="fictional CSV under data/local-test/ only")
    mode.add_argument("--check-setup", action="store_true", help="read-only SMTP/TLS/DNS checks, no login/mail")
    parser.add_argument("--csv", default="data/contacts.csv", help="saved dates/state; never allocates schedules")
    parser.add_argument("--channel", choices=("all", *CHANNELS), default="all")
    parser.add_argument("--mailpit-port", type=int, default=1026)
    parser.add_argument("--sender", default="research@example.invalid", help="local-test From header only")
    parser.add_argument("--now", help="aware simulation timestamp for local tests/read-only checks")
    args = parser.parse_args(argv)
    try:
        if args.check_setup:
            if args.now:
                raise ValueError("--now is only for reports/local fixtures.")
            return check_setup()
        path = workspace_path(args.csv)
        fixed = parse_timestamp(args.now) if args.now else None
        channels = CHANNELS if args.channel == "all" else (args.channel,)
        if args.local_test:
            run_local(path, port=args.mailpit_port, sender=args.sender,
                      clock=(lambda: fixed) if fixed else None, channels=channels)
            return 0
        store = ContactFile(path)
        now = fixed or datetime.now(UTC)
        print_counters(counters(store.rows, now), "READ-ONLY REPORT" if args.report else "CSV DATE CHECK / REAL DELIVERY DISABLED")
        if not args.report:
            if not working(now):
                print("Nothing due outside working hours or on weekends.")
            for channel in channels:
                selected = due_candidates(store.rows, channel, now)
                print(f"Due {channel} contacts now: {len(selected)}; IDs: {', '.join(row['id'] for row in selected) or '-'}")
            print("Dates come only from the CSV. Real delivery still requires separate approval.")
        return 0
    except (OSError, ValueError) as error:
        print(f"Outreach stopped: {error}")
        return 1
    except KeyboardInterrupt:
        print("Interrupted. Review any sending state manually before resetting; no automatic resend.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
