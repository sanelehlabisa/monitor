"""FastAPI application entry point."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app import __version__
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
    application.state.settings = application_settings

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """Report process health without querying external dependencies."""

        return HealthResponse(
            service="monitor-api",
            version=__version__,
            environment=application_settings.environment,
        )

    return application


app = create_app()
