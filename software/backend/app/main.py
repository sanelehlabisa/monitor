"""FastAPI application entry point."""

from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import __version__
from app.auth_api import router as auth_router
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
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.state.settings = application_settings
    application.include_router(auth_router)

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
