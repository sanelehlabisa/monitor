"""FastAPI application entry point."""

from typing import Annotated, Literal

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import __version__
from app.auth import AuthenticatedUser, TokenValidator, require_identity
from app.settings import Settings


class HealthResponse(BaseModel):
    """Stable process-health response returned to local tooling."""

    status: Literal["ok"] = "ok"
    service: str
    version: str
    environment: str


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a configured Monitor API application."""

    application_settings = settings or Settings()
    application = FastAPI(title="Monitor API", version=__version__)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[application_settings.cors_origin],
        allow_methods=["GET"],
        allow_headers=["Authorization", "Content-Type"],
    )
    application.state.settings = application_settings
    application.state.token_validator = TokenValidator(application_settings)

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """Report process health without querying external dependencies."""

        return HealthResponse(
            service="monitor-api",
            version=__version__,
            environment=application_settings.environment,
        )

    @application.get("/auth/me", response_model=AuthenticatedUser)
    def auth_me(
        identity: Annotated[AuthenticatedUser, Depends(require_identity)],
    ) -> AuthenticatedUser:
        """Return identity claims from a validated user access token."""

        return identity

    return application


app = create_app()
