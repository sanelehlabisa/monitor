"""Unit tests for safe login-message construction and SMTP modes."""

from email.message import EmailMessage
from email import policy
from email.parser import BytesParser
from typing import Any

from app.modules.email_delivery import (
    EmailDeliveryError,
    SmtpEmailSender,
    build_login_code_message,
)
from pytest import MonkeyPatch, raises


class FakeSmtpClient:
    """Record standard-library SMTP calls without using a network."""

    def __init__(self, supports_starttls: bool = False) -> None:
        self.supports_starttls = supports_starttls
        self.calls: list[Any] = []

    def __enter__(self) -> "FakeSmtpClient":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def ehlo(self) -> None:
        self.calls.append("ehlo")

    def has_extn(self, extension: str) -> bool:
        self.calls.append(("has_extn", extension))
        return self.supports_starttls

    def starttls(self, context: object) -> None:
        self.calls.append(("starttls", context))

    def login(self, username: str, password: str) -> None:
        self.calls.append(("login", username, password))

    def send_message(self, message: EmailMessage) -> None:
        self.calls.append(("send_message", message))


def test_login_message_has_html_and_plain_text_and_normalizes_recipient() -> None:
    """MIME delivery preserves the code, expiry and personal-use guidance."""

    message = build_login_code_message(
        " User@Example.TEST ", "012345", "login@monitor.local"
    )
    message = BytesParser(policy=policy.default).parsebytes(message.as_bytes())

    assert message["To"] == "user@example.test"
    assert message["From"] == "login@monitor.local"
    assert message["Subject"] == "Your Roventics Monitor sign-in code"
    assert message.get_content_type() == "multipart/alternative"
    assert [part.get_content_type() for part in message.iter_parts()] == ["text/plain", "text/html"]
    for kind in ("plain", "html"):
        body = message.get_body(preferencelist=(kind,)).get_content()
        assert "012345" in body
        assert "10 minutes" in body
        assert "Do not share this code with anyone" in body
        assert "Use it only to sign in yourself" in body
        assert "ignore this email" in body
        assert "The Roventics team" in body
    html = message.get_body(preferencelist=("html",)).get_content()
    assert "<script" not in html and "<button" not in html
    assert "https://roventics.com/images/logo.png" in html
    assert 'href="https://roventics.com"' in html


def test_login_html_escapes_interpolated_content() -> None:
    """Unexpected code content cannot become active HTML or a link."""
    message = build_login_code_message("user@example.test", "<b>&012345", "login@monitor.local")
    assert "&lt;b&gt;&amp;012345" in message.get_body(preferencelist=("html",)).get_content()
    assert "<b>&012345" in message.get_body(preferencelist=("plain",)).get_content()


def test_plain_smtp_sends_without_credentials(monkeypatch: MonkeyPatch) -> None:
    """Mailpit-style SMTP works without TLS or authentication."""

    client = FakeSmtpClient()
    monkeypatch.setattr(
        "app.modules.email_delivery.smtplib.SMTP", lambda *args, **kwargs: client
    )

    SmtpEmailSender().send(EmailMessage())

    assert [call[0] for call in client.calls if isinstance(call, tuple)] == [
        "has_extn",
        "send_message",
    ]


def test_starttls_precedes_authenticated_delivery(monkeypatch: MonkeyPatch) -> None:
    """Credentials are used only after an advertised STARTTLS upgrade."""

    client = FakeSmtpClient(supports_starttls=True)
    monkeypatch.setattr(
        "app.modules.email_delivery.smtplib.SMTP", lambda *args, **kwargs: client
    )
    monkeypatch.setenv("SMTP_USER", "monitor")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")

    SmtpEmailSender().send(EmailMessage())

    names = [call if isinstance(call, str) else call[0] for call in client.calls]
    assert names == ["ehlo", "has_extn", "starttls", "ehlo", "login", "send_message"]


def test_implicit_tls_supports_authenticated_delivery(monkeypatch: MonkeyPatch) -> None:
    """SMTP_SECURE selects SMTP over implicit TLS."""

    client = FakeSmtpClient()
    monkeypatch.setattr(
        "app.modules.email_delivery.smtplib.SMTP_SSL", lambda *args, **kwargs: client
    )
    monkeypatch.setenv("SMTP_SECURE", "true")
    monkeypatch.setenv("SMTP_USER", "monitor")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")

    SmtpEmailSender().send(EmailMessage())

    assert [call[0] for call in client.calls] == ["login", "send_message"]


def test_credentials_are_rejected_without_encryption(monkeypatch: MonkeyPatch) -> None:
    """A server cannot cause credentials to be sent over plaintext SMTP."""

    client = FakeSmtpClient()
    monkeypatch.setattr(
        "app.modules.email_delivery.smtplib.SMTP", lambda *args, **kwargs: client
    )
    monkeypatch.setenv("SMTP_USER", "monitor")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")

    with raises(EmailDeliveryError, match="requires TLS"):
        SmtpEmailSender().send(EmailMessage())

    assert not any(
        call[0] == "login" for call in client.calls if isinstance(call, tuple)
    )
