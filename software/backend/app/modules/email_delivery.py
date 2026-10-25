"""Build and deliver passwordless login messages through SMTP."""

from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from html import escape
import os
import smtplib
import ssl
from typing import Any, Protocol
from uuid import UUID

from psycopg import Connection

from app.modules.otp import OTP_TTL, get_otp_secret, invalidate_otp_challenge, issue_otp, normalize_email


class EmailDeliveryError(Exception):
    """Raised when a login email cannot be delivered safely."""


class EmailSender(Protocol):
    """Small boundary implemented by SMTP and test senders."""

    def send(self, message: EmailMessage) -> None:
        """Deliver one prepared email message."""


@dataclass(frozen=True)
class OtpDelivery:
    """Safe challenge metadata returned after successful delivery."""

    challenge_id: UUID
    expires_at: datetime


class SmtpEmailSender:
    """Deliver email using implicit TLS or opportunistic STARTTLS."""

    def __init__(self) -> None:
        self.smtp_host = os.environ["SMTP_HOST"]
        try:
            self.smtp_port = int(os.environ["SMTP_PORT"])
            if not 1 <= self.smtp_port <= 65535:
                raise ValueError
        except ValueError:
            raise ValueError("SMTP_PORT must be an integer from 1 to 65535") from None
        secure = os.environ["SMTP_SECURE"].lower()
        if secure not in {"0", "1", "false", "true", "f", "t", "no", "yes", "n", "y", "off", "on"}:
            raise ValueError("SMTP_SECURE must be a boolean")
        self.smtp_secure = secure in {"1", "true", "t", "yes", "y", "on"}
        self.smtp_user = os.environ["SMTP_USER"]
        self.smtp_password = os.environ["SMTP_PASSWORD"]

    def send(self, message: EmailMessage) -> None:
        """Send a message without leaking credentials or message contents."""

        try:
            if self.smtp_secure:
                with smtplib.SMTP_SSL(
                    self.smtp_host,
                    self.smtp_port,
                    timeout=10,
                    context=ssl.create_default_context(),
                ) as client:
                    self._authenticate_and_send(client, message, encrypted=True)
                return

            with smtplib.SMTP(
                self.smtp_host, self.smtp_port, timeout=10
            ) as client:
                client.ehlo()
                encrypted = False
                if client.has_extn("starttls"):
                    client.starttls(context=ssl.create_default_context())
                    client.ehlo()
                    encrypted = True
                self._authenticate_and_send(client, message, encrypted)
        except EmailDeliveryError:
            raise
        except (OSError, smtplib.SMTPException) as error:
            raise EmailDeliveryError("Login email delivery failed") from error

    def _authenticate_and_send(
        self, client: smtplib.SMTP, message: EmailMessage, encrypted: bool
    ) -> None:
        """Authenticate only over encryption, then send the prepared message."""

        username = self.smtp_user
        password = self.smtp_password
        if bool(username) != bool(password):
            raise EmailDeliveryError("SMTP credentials are incomplete")
        if username:
            if not encrypted:
                raise EmailDeliveryError("SMTP authentication requires TLS")
            client.login(username, password)
        client.send_message(message)


def build_login_code_message(recipient: str, code: str, sender: str) -> EmailMessage:
    """Create a readable login email with a plain-text fallback."""

    expires_in = int(OTP_TTL.total_seconds() // 60)
    safe_code = escape(code)
    message = EmailMessage()
    message["From"] = sender
    message["To"] = normalize_email(recipient)
    message["Subject"] = "Your Roventics Monitor sign-in code"
    message.set_content(
        f"Your Roventics Monitor sign-in code is {code}.\n\n"
        f"It expires in {expires_in} minutes.\n\n"
        "Do not share this code with anyone. Use it only to sign in yourself.\n\n"
        "If you did not request this code, you can ignore this email.\n\n"
        "The Roventics team\nRoventics (Pty) Ltd\nhttps://roventics.com\n"
    )
    message.add_alternative(
        f"""<!doctype html>
<html lang="en"><body style="margin:0;padding:0;background-color:#f4f4f4;color:#111;font-family:Arial,sans-serif;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background-color:#fff;border:1px solid #ddd;">
<tr><td style="padding:24px;">
<h1 style="margin:0 0 16px;font-size:22px;line-height:1.3;">Sign in to Monitor</h1>
<p style="margin:0 0 20px;font-size:15px;line-height:1.5;">Enter this code in Monitor to sign in.</p>
<p style="margin:0 0 20px;padding:20px;background-color:#f2f2f2;text-align:center;font-family:monospace;font-size:32px;font-weight:700;letter-spacing:4px;">{safe_code}</p>
<p style="margin:0 0 16px;font-size:15px;">Expires in {expires_in} minutes.</p>
<p style="margin:0 0 16px;font-size:15px;line-height:1.5;">Do not share this code with anyone. Use it only to sign in yourself.</p>
<p style="margin:0;color:#555;font-size:13px;line-height:1.5;">If you did not request this code, you can ignore this email.</p>
</td></tr>
<tr><td style="padding:20px 24px;border-top:1px solid #ddd;">
<table role="presentation" cellspacing="0" cellpadding="0"><tr>
<td style="padding-right:12px;"><img src="https://roventics.com/images/logo.png" width="32" height="32" alt="Roventics" style="display:block;border:0;"></td>
<td style="font-size:13px;line-height:1.6;color:#555;"><strong style="color:#111;">The Roventics team</strong><br>
Roventics (Pty) Ltd &middot; <a href="https://roventics.com" style="color:#111;">roventics.com</a></td>
</tr></table>
</td></tr></table>
</td></tr></table>
</body></html>""",
        subtype="html",
    )
    return message


def deliver_login_code(
    connection: Connection[Any],
    email: str,
    sender: EmailSender | None = None,
    now: datetime | None = None,
) -> OtpDelivery:
    """Issue an OTP and return safe metadata only after its email is sent."""

    issued = issue_otp(
        connection,
        email,
        get_otp_secret(),
        now,
    )
    message = build_login_code_message(email, issued.code, os.environ["EMAIL_FROM"])
    try:
        (sender or SmtpEmailSender()).send(message)
    except EmailDeliveryError:
        invalidate_otp_challenge(connection, issued.challenge_id, now)
        raise
    return OtpDelivery(issued.challenge_id, issued.expires_at)
