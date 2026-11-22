"""Send due CSV contacts using research .env, at most five per channel/day."""

import argparse
from collections import Counter, deque
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage
from email.policy import SMTP as SMTP_POLICY
from email.utils import format_datetime
import hashlib
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import smtplib
import re
import ssl
import uuid
from typing import Any, Callable
from urllib.parse import urlsplit

import phonenumbers

from pipeline import (CONTACT_FIELDS, WORKSPACE, RegisterError, atomic_write, csv_bytes, guarded_write,
                      load_contacts, normalize_email, normalize_phone, single_writer, workspace_path)


UTC = timezone.utc
LOCAL = timezone(timedelta(hours=2), "Africa/Johannesburg")
CHANNELS = ("email", "sms")
STATUSES = {"new", "scheduled", "sending", "sent", "failed", "skipped"}
DAILY_CAP, MAX_ATTEMPTS = 5, 3
Row = dict[str, str]


def mock_smtp(values: dict[str, str]) -> bool:
    return values.get("SMTP_HOST", "").lower() in {"127.0.0.1", "localhost", "::1"}


def validate_smtp(values: dict[str, str]) -> None:
    try:
        port = int(values.get("SMTP_PORT", "0"))
    except ValueError:
        raise ValueError("SMTP_PORT must be a number.") from None
    host = values.get("SMTP_HOST", "")
    if (not host or (not mock_smtp(values) and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", host))
            or not 1 <= port <= 65535 or values.get("SMTP_SECURE") not in {"true", "false"}):
        raise ValueError("Set a valid SMTP_HOST, SMTP_PORT and SMTP_SECURE in research .env.")
    if not mock_smtp(values) and not (values.get("SMTP_USER") and values.get("SMTP_PASSWORD")):
        raise ValueError("Non-loopback SMTP requires this research account's username/password and verified TLS.")


def load_config() -> dict[str, str]:
    from dotenv import dotenv_values
    values = {k: v or "" for k, v in dotenv_values(WORKSPACE / ".env", interpolate=False).items()}
    validate_smtp(values)
    if not normalize_email(values.get("RESEARCH_EMAIL_FROM", "")) or not values.get("CONTACTS_CSV"):
        raise ValueError("Set RESEARCH_EMAIL_FROM and CONTACTS_CSV in market-research/.env.")
    return values


def sms_mock_port(values: dict[str, str]) -> int | None:
    value = values.get("SMS_GATEWAY_URL", "")
    if not value:
        return None
    parsed = urlsplit(value)
    if (parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parsed.path != "/messages" or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.port is None or not 1 <= parsed.port <= 65535):
        raise ValueError("SMS is mock-only: use a loopback http://host:port/messages URL or leave it blank.")
    return parsed.port


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
             outcome: str = "success", mock_port: int | None = None) -> str:
    """Offline by default; an explicit port permits only the loopback HTTP mock."""
    if outcome not in {"success", "temporary", "permanent", "uncertain"}:
        raise ValueError("Unknown mock outcome.")
    if mock_port is not None:
        return send_sms_local_http(phone_number, message, mock_port, outcome)
    if outcome != "success":
        raise DeliveryError("Local SMS mock: " + outcome, outcome)
    receipt = "mock-" + hashlib.sha256((phone_number + message).encode()).hexdigest()[:20]
    if capture is not None:
        append_log(capture, {"mode": "offline_mock", "receipt": receipt, "phone": phone_number, "message": message})
    return receipt


def send_sms_local_http(phone: str, message: str, port: int, outcome: str = "success") -> str:
    if not 1 <= port <= 65535:
        raise ValueError("Invalid local SMS mock port.")
    client = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    submitted = False
    try:
        client.connect()
        submitted = True
        client.request("POST", "/messages", json.dumps({"phone": phone, "message": message,
                       "source_domain": "example.invalid", "outcome": outcome}),
                       {"Content-Type": "application/json"})
        response = client.getresponse()
        raw = response.read(4097)
        if len(raw) > 4096:
            raise ValueError("Oversized SMS mock response.")
        result = json.loads(raw)
        if isinstance(result, dict) and result.get("mode") == "http_mock":
            receipt = result.get("receipt", "")
            if response.status == 201 and result.get("accepted") is True and isinstance(receipt, str) and re.fullmatch(r"mock-[0-9a-f]{32}", receipt):
                return receipt
            if result.get("accepted") is False and response.status in {400, 403, 404, 413, 415, 422, 503}:
                raise DeliveryError(f"Local SMS API rejected request ({response.status})",
                                    "temporary" if response.status == 503 else "permanent")
        raise DeliveryError("Unconfirmed SMS API acceptance; review mock captures.", "uncertain")
    except (OSError, http.client.HTTPException, ValueError):
        raise DeliveryError("Local SMS API connection/response interrupted",
                            "uncertain" if submitted else "temporary") from None
    finally:
        client.close()


def serve_mock_sms(port: int = 8086, bind: str = "127.0.0.1") -> None:
    """Capture-only API; no account configuration, forwarding or real SMS adapter."""
    if not 1 <= port <= 65535 or bind not in {"127.0.0.1", "0.0.0.0"}:
        raise ValueError("Invalid SMS mock binding.")
    capture = workspace_path("data/local-test/compose/sms-api/messages.jsonl")
    capture.parent.mkdir(parents=True, exist_ok=True)

    class Handler(BaseHTTPRequestHandler):
        def setup(self) -> None:
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, format: str, *args: Any) -> None:
            pass  # Never echo request bodies, phone numbers or arbitrary paths.

        def reply(self, code: int, payload: dict[str, Any]) -> None:
            content = json.dumps({"mode": "http_mock", **payload}).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)

        def allowed(self) -> bool:
            hosts = {f"{host}:{p}" for host in ("localhost", "127.0.0.1", "mock-sms") for p in (port, 8086)}
            if self.headers.get("Origin") or self.headers.get("Host") not in hosts:
                self.reply(403, {"accepted": False, "error": "Local mock clients only."})
                return False
            return True

        def do_GET(self) -> None:
            if not self.allowed():
                return
            if self.path == "/health":
                self.reply(200, {"healthy": True, "real_delivery": False})
            elif self.path == "/messages":
                try:
                    recent: deque[dict[str, Any]] = deque(maxlen=100)
                    count = 0
                    if capture.exists():
                        with capture.open(encoding="utf-8") as source:
                            for line in source:
                                recent.append(json.loads(line))
                                count += 1
                    self.reply(200, {"count": count, "messages": list(recent)})
                except (OSError, ValueError):
                    self.reply(503, {"error": "Capture unavailable; review local files."})
            else:
                self.reply(404, {"accepted": False, "error": "Use /health or /messages."})

        def do_POST(self) -> None:
            if not self.allowed():
                return
            if self.path != "/messages":
                self.reply(404, {"accepted": False, "error": "Use /messages."})
                return
            if self.headers.get_content_type() != "application/json":
                self.reply(415, {"accepted": False, "error": "JSON required."})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if self.headers.get("Transfer-Encoding") or not 0 < size <= 65536:
                    self.reply(413, {"accepted": False, "error": "Body must be 1-65536 bytes."})
                    return
                value = json.loads(self.rfile.read(size))
                if not isinstance(value, dict) or set(value) - {"phone", "message", "source_domain", "outcome"}:
                    raise ValueError
                phone, message, outcome = value.get("phone"), value.get("message"), value.get("outcome", "success")
                if (value.get("source_domain") != "example.invalid" or not isinstance(phone, str)
                        or normalize_phone(phone, True)[0] != phone or not isinstance(message, str)
                        or not message.strip() or "\x00" in message or len(message.encode()) > 32768
                        or outcome not in {"success", "temporary", "permanent", "uncertain"}):
                    raise ValueError
            except (ValueError, TypeError, UnicodeError):
                self.reply(400, {"accepted": False, "error": "Invalid fictional mock payload."})
                return
            if outcome in {"temporary", "permanent"}:
                self.reply(503 if outcome == "temporary" else 422, {"accepted": False, "error": "Controlled mock rejection."})
                return
            receipt = "mock-" + uuid.uuid4().hex
            try:
                append_log(capture, {"mode": "http_mock", "receipt": receipt, "phone": phone,
                                    "message": message, "at": timestamp(datetime.now(UTC))})
            except OSError:
                # Partial persistence is possible; do not claim safe rejection/retry.
                self.reply(500, {"error": "Capture persistence uncertain; review manually."})
                return
            if outcome == "uncertain":
                self.close_connection = True  # Accept then drop the response for restart-safety checks.
                return
            self.reply(201, {"accepted": True, "receipt": receipt})

    with HTTPServer((bind, port), Handler) as server:
        print(f"SMS capture-only API on {bind}:{port}; no real delivery.", flush=True)
        server.serve_forever()


def send_email_local(recipient: str, sender: str, identity: str, port: int,
                     *, template: tuple[str, str] | None = None) -> str:
    return send_email(recipient, sender, identity,
                      {"SMTP_HOST": "127.0.0.1", "SMTP_PORT": str(port), "SMTP_SECURE": "false"}, template=template)


def send_email(recipient: str, sender: str, identity: str, values: dict[str, str],
               *, template: tuple[str, str] | None = None) -> str:
    validate_smtp(values)
    local = mock_smtp(values)
    if (not normalize_email(sender) or normalize_email(recipient) != recipient
            or (local and not recipient.endswith(".invalid"))):
        raise ValueError("Invalid email address; loopback SMTP accepts fictional recipients only.")
    subject, body = template or load_templates()[:2]
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = sender, recipient, subject
    message["Date"] = format_datetime(datetime.now(UTC))
    digest = hashlib.sha256((identity + recipient + subject + body).encode()).hexdigest()[:24]
    receipt = f"<research-{digest}@{sender.rsplit('@', 1)[1]}>"
    message["Message-ID"] = receipt
    message.set_content(body)
    client: smtplib.SMTP | None = None
    stage = "connect"
    try:
        # Supply host at construction so TLS hostname/SNI verification uses it.
        client = (smtplib.SMTP_SSL(values["SMTP_HOST"], int(values["SMTP_PORT"]), timeout=10, context=ssl.create_default_context())
                  if values["SMTP_SECURE"] == "true" else smtplib.SMTP(values["SMTP_HOST"], int(values["SMTP_PORT"]), timeout=10))
        client.ehlo_or_helo_if_needed()
        if not local:
            if values["SMTP_SECURE"] == "false":
                if not client.has_extn("starttls"):
                    raise DeliveryError("SMTP requires STARTTLS; credentials were not submitted.", "permanent")
                client.starttls(context=ssl.create_default_context())
                client.ehlo()
            client.login(values["SMTP_USER"], values["SMTP_PASSWORD"])
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
    except ssl.SSLError:
        raise DeliveryError("SMTP TLS connection failed; no downgrade permitted.", "uncertain" if stage == "data" else "permanent") from None
    except UnicodeError:
        raise DeliveryError("SMTP text/credential encoding failed.", "uncertain" if stage == "data" else "permanent") from None
    except (OSError, smtplib.SMTPException):
        raise DeliveryError("SMTP connection interrupted", "uncertain" if stage == "data" else "temporary") from None
    finally:
        # A failed QUIT must never turn confirmed DATA acceptance into a resend.
        if client is not None:
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
    return (row[f"{channel}_status"] in {"new", "scheduled"} and scheduled is not None
            and scheduled.astimezone(LOCAL).date() <= now.astimezone(LOCAL).date()
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


def run_messages(path: Path, *, port: int = 1026, sender: str = "research@example.invalid",
              clock: Callable[[], datetime] | None = None, channels: tuple[str, ...] = CHANNELS,
              sms_port: int | None = None, smtp: dict[str, str] | None = None) -> dict[str, int]:
    if not normalize_email(sender) or not 1 <= port <= 65535 or not channels or any(channel not in CHANNELS for channel in channels):
        raise ValueError("Invalid local delivery configuration.")
    if sms_port is not None and not 1 <= sms_port <= 65535:
        raise ValueError("Invalid local SMS mock port.")
    local = smtp is None or mock_smtp(smtp)
    if smtp is not None:
        validate_smtp(smtp)
    if not local and (clock is not None or "sms" in channels):
        raise ValueError("Configured real SMTP uses the actual clock and email only; live SMS is unavailable.")
    clock = clock or (lambda: datetime.now(UTC))
    path = workspace_path(str(path))
    sent_run: Counter[str] = Counter()
    failed_run: Counter[str] = Counter()
    with single_writer(workspace_path("data/contacts.lock")):
        store = ContactFile(path)
        if local:
            require_test_csv(path, store.rows)
        elif not path.samefile(workspace_path("data/contacts.csv")):
            raise ValueError("Real SMTP requires CONTACTS_CSV=data/contacts.csv; mock state cannot be used for live mail.")
        subject, email_body, sms_body = load_templates()
        for channel in channels:
            if channel not in CHANNELS:
                raise ValueError("Unknown channel.")
            ordered = due_candidates(store.rows, channel, clock())
            for row in ordered:
                now = clock()
                if day_usage(store.rows, channel, now) >= DAILY_CAP:
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
                    if channel == "sms":
                        receipt = send_sms(row["phone"], sms_body, capture=path.parent / "sms-capture.jsonl", mock_port=sms_port)
                    elif smtp is None:
                        receipt = send_email_local(row["email"], sender, row["id"], port, template=(subject, email_body))
                    else:
                        receipt = send_email(row["email"], sender, row["id"], smtp, template=(subject, email_body))
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
        print_counters(result, "MAILPIT / SMS MOCK" if local else "CONFIGURED SMTP / SMS DISABLED")
        return result


run_local = run_messages  # Existing local walkthroughs share the same state machine.


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
    values = load_config()
    if mock_smtp(values):
        print("Mailpit configuration selected; fictional CSV only. No authentication or mail submitted.")
        return 0
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
              "sender_authorization": "unverified; this inspection performs no authentication or sending",
              "tls": inspect_tls(values["SMTP_HOST"] or "", port, secure == "true"),
              "dns": inspect_dns(sender.rsplit("@", 1)[1], selector),
              "smtp_delivery_implemented": True,
              "notes": ["Published policies are not proof of alignment, valid authorization or actual DKIM signing.",
                        "Review all unverified/missing policies and sender permission before production approval."]}
    report["blockers"] = readiness_blockers(report)
    target = workspace_path("data/email-readiness.json")
    atomic_write(target, json.dumps(report, indent=2).encode())
    print("Read-only readiness report: data/email-readiness.json")
    print("TLS: " + report["tls"]["status"])
    for label, result in report["dns"].items():
        print(label.upper() + ": " + result["status"])
    print("Sender authorization/actual signing unverified. This inspection submitted no mail.")
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
    mode.add_argument("--preview", action="store_true", help="read-only due selection, no delivery")
    mode.add_argument("--local-test", action="store_true", help="fictional CSV under data/local-test/ only")
    mode.add_argument("--check-setup", action="store_true", help="read-only SMTP/TLS/DNS checks, no login/mail")
    mode.add_argument("--mock-sms-api", action="store_true", help="run a capture-only SMS HTTP service")
    parser.add_argument("--csv", help="override .env CONTACTS_CSV; never allocates schedules")
    parser.add_argument("--channel", choices=("all", *CHANNELS), default="all")
    parser.add_argument("--mailpit-port", type=int, default=1026)
    parser.add_argument("--mock-sms-port", type=int, help="explicit loopback SMS API port; otherwise offline mock")
    parser.add_argument("--mock-sms-bind", choices=("127.0.0.1", "0.0.0.0"), default="127.0.0.1",
                        help="server binding only; Compose publishes exclusively on loopback")
    parser.add_argument("--sender", default="research@example.invalid", help="local-test From header only")
    parser.add_argument("--now", help="aware simulation timestamp for local tests/read-only checks")
    args = parser.parse_args(argv)
    try:
        if args.mock_sms_api:
            if args.now:
                raise ValueError("Server mode uses the real clock.")
            serve_mock_sms(8086 if args.mock_sms_port is None else args.mock_sms_port, args.mock_sms_bind)
            return 0
        if args.check_setup:
            if args.now:
                raise ValueError("--now is only for reports/local fixtures.")
            return check_setup()
        fixed = parse_timestamp(args.now) if args.now else None
        channels = CHANNELS if args.channel == "all" else (args.channel,)
        if args.local_test:
            if not args.csv:
                raise ValueError("The explicit --local-test walkthrough requires --csv.")
            path = workspace_path(args.csv)
            run_local(path, port=args.mailpit_port, sender=args.sender,
                      clock=(lambda: fixed) if fixed else None, channels=channels, sms_port=args.mock_sms_port)
            return 0
        if args.mock_sms_port is not None:
            raise ValueError("Normal sending reads SMS_GATEWAY_URL from research .env.")
        values = load_config()
        path = workspace_path(args.csv or values["CONTACTS_CSV"])
        if args.report or args.preview:
            store = ContactFile(path)
            now = fixed or datetime.now(UTC)
            print_counters(counters(store.rows, now), "READ-ONLY REPORT" if args.report else "READ-ONLY PREVIEW")
            if args.preview:
                for channel in channels:
                    print(f"Due {channel} contacts: {len(due_candidates(store.rows, channel, now))}")
            return 0
        if not mock_smtp(values):
            if args.channel == "sms":
                raise ValueError("Live SMS needs a selected gateway/API; only email delivery is implemented.")
            channels = ("email",)
        run_messages(path, sender=values["RESEARCH_EMAIL_FROM"], smtp=values, channels=channels,
                     sms_port=sms_mock_port(values) if mock_smtp(values) and "sms" in channels else None,
                     clock=(lambda: fixed) if fixed else None)
        return 0
    except (OSError, ValueError) as error:
        print(f"Outreach stopped: {error}")
        return 1
    except KeyboardInterrupt:
        print("Interrupted. Review any sending state manually before resetting; no automatic resend.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
