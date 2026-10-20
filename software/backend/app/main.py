"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.endpoints.auth import router as auth_router
from app.endpoints.ledger import router as ledger_router
from app.endpoints.meters import router as meter_router
from app.endpoints.reminders import router as reminder_router
from app.modules.reminder_scheduler import monthly_reminder_lifespan
from app.schemas.health import HealthResponse
from app.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a configured Monitor API application."""

    application_settings = settings or Settings()
    application = FastAPI(
        title="Monitor API", version=__version__,
        lifespan=lambda app: monthly_reminder_lifespan(app, application_settings),
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[application_settings.cors_origin],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type"],
    )
    application.state.settings = application_settings
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
            environment=application_settings.environment,
        )

    return application


app = create_app()
