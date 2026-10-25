"""Build and deliver passwordless login messages through SMTP."""

from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
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
    """Create a plain-text message for one normalized email recipient."""

    message = EmailMessage()
    message["From"] = sender
    message["To"] = normalize_email(recipient)
    message["Subject"] = "Your Roventics Monitor sign-in code"
    message.set_content(
        f"Your Roventics Monitor sign-in code is {code}.\n\n"
        f"It expires in {int(OTP_TTL.total_seconds() // 60)} minutes. "
        "Do not share this code.\n\n"
        "If you did not request this code, you can ignore this email.\n"
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
