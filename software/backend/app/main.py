"""FastAPI application entry point."""

from ipaddress import IPv4Address
import os
import re
from urllib.parse import urlsplit

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.endpoints.auth import router as auth_router
from app.endpoints.ledger import router as ledger_router
from app.endpoints.meters import router as meter_router
from app.endpoints.reminders import router as reminder_router
from app.modules.email_delivery import SmtpEmailSender
from app.modules.otp import get_otp_secret
from app.modules.reminder_scheduler import monthly_reminder_lifespan, read_activation_cutoff
from app.schemas.health import HealthResponse


def validate_origin(value: str, environment: str) -> str:
    """Keep one canonical browser origin without reflecting invalid input."""
    try:
        if not re.fullmatch(r"https?://[a-z0-9.-]+(?::[0-9]+)?", value):
            raise ValueError
        origin = urlsplit(value)
        host = origin.hostname or ""
        label = r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
        if re.fullmatch(r"[0-9.]+", host):
            IPv4Address(host)
        elif not re.fullmatch(rf"(?:{label}\.)*[a-z](?:[a-z0-9-]{{0,61}}[a-z0-9])?", host):
            raise ValueError
        port = origin.port
        authority = host + (f":{port}" if port is not None else "")
        if (len(host) > 253 or port == 0 or port == (443 if origin.scheme == "https" else 80)
                or value != f"{origin.scheme}://{authority}"):
            raise ValueError
    except ValueError:
        raise ValueError("APP_URL must be a canonical HTTP(S) origin") from None
    if environment == "production" and origin.scheme != "https":
        raise ValueError("Production APP_URL must use HTTPS")
    return value


def create_app() -> FastAPI:
    """Create a configured Monitor API application."""

    environment = os.environ["MONITOR_ENVIRONMENT"]
    if environment not in {"development", "test", "production"}:
        raise ValueError("MONITOR_ENVIRONMENT must be development, test or production")
    cors_origin = validate_origin(os.environ["MONITOR_CORS_ORIGIN"], environment)
    # Require request-handler values now, without opening a DB or SMTP connection.
    for name in ("MONITOR_DATABASE_URL", "EMAIL_FROM"):
        if name not in os.environ:
            raise KeyError(name)
    get_otp_secret()
    SmtpEmailSender()  # Validate SMTP values without connecting or sending.
    activation_at = read_activation_cutoff()
    application = FastAPI(
        title="Monitor API", version=__version__,
        lifespan=lambda app: monthly_reminder_lifespan(app, activation_at),
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[cors_origin],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type"],
    )
    application.include_router(auth_router)
    application.include_router(meter_router)
    application.include_router(ledger_router)
    application.include_router(reminder_router)

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """Report process health without querying external dependencies."""

        return HealthResponse(
            service="monitor-api",
            version=__version__,
            environment=environment,
        )

    return application


app = create_app()
