"""FastAPI routes for passwordless human authentication."""

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, field_validator

from app.database import connect_database
from app.email_delivery import EmailDeliveryError, deliver_login_code
from app.otp import (
    OtpRateLimitError,
    OtpVerificationError,
    User,
    normalize_email,
    verify_otp,
)
from app.sessions import (
    SESSION_TTL,
    CreatedSession,
    SessionAuthenticationError,
    authenticate_session,
    create_session,
    revoke_session,
)
from app.settings import Settings

COOKIE_NAME = "monitor_session"
REQUEST_ACCEPTED_MESSAGE = (
    "If the address can receive email, a sign-in code has been sent."
)
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+$"

router = APIRouter(prefix="/api")


class EmailRequest(BaseModel):
    """Normalized email supplied to the passwordless flow."""

    email: str = Field(min_length=3, max_length=254, pattern=EMAIL_PATTERN)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_input_email(cls, value: object) -> object:
        """Normalize string inputs before applying the practical shape check."""

        return normalize_email(value) if isinstance(value, str) else value


class VerifyOtpRequest(EmailRequest):
    """Email and six-digit code submitted for verification."""

    code: str = Field(pattern=r"^\d{6}$")


class AcceptedResponse(BaseModel):
    """Enumeration-safe response for valid OTP request shapes."""

    message: str


class UserResponse(BaseModel):
    """Safe authenticated-user representation."""

    id: int
    email: str


@router.post(
    "/auth/request-otp",
    response_model=AcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def request_otp(payload: EmailRequest, request: Request) -> AcceptedResponse:
    """Request a code without exposing policy or delivery outcomes."""

    settings = _settings(request)
    try:
        with connect_database(settings) as connection:
            deliver_login_code(connection, payload.email, settings)
    except (OtpRateLimitError, EmailDeliveryError):
        pass
    return AcceptedResponse(message=REQUEST_ACCEPTED_MESSAGE)


@router.post("/auth/verify-otp", response_model=UserResponse)
def verify_code(
    payload: VerifyOtpRequest, request: Request, response: Response
) -> UserResponse:
    """Verify the newest code and establish an opaque cookie session."""

    settings = _settings(request)
    try:
        with connect_database(settings) as connection:
            user = verify_otp(
                connection,
                payload.email,
                payload.code,
                settings.otp_hmac_secret.get_secret_value(),
            )
            session = create_session(connection, user.id)
    except OtpVerificationError as error:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid or expired code"
        ) from error

    _set_session_cookie(response, session, settings)
    return _user_response(user)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response) -> None:
    """Revoke only the presented session and always clear its cookie."""

    settings = _settings(request)
    token = request.cookies.get(COOKIE_NAME)
    if token:
        try:
            with connect_database(settings) as connection:
                revoke_session(connection, token)
        except SessionAuthenticationError:
            pass
    response.delete_cookie(
        COOKIE_NAME,
        path="/",
        secure=_cookie_is_secure(settings),
        httponly=True,
        samesite="lax",
    )


@router.get("/me", response_model=UserResponse)
def current_user(request: Request) -> UserResponse:
    """Return the user authenticated by the opaque session cookie."""

    token = request.cookies.get(COOKIE_NAME)
    try:
        if not token:
            raise SessionAuthenticationError("Session is unavailable")
        with connect_database(_settings(request)) as connection:
            user = authenticate_session(connection, token)
    except SessionAuthenticationError as error:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Authentication required"
        ) from error
    return _user_response(user)


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _cookie_is_secure(settings: Settings) -> bool:
    return settings.environment != "development"


def _set_session_cookie(
    response: Response, session: CreatedSession, settings: Settings
) -> None:
    response.set_cookie(
        COOKIE_NAME,
        session.token,
        max_age=int(SESSION_TTL.total_seconds()),
        expires=session.expires_at,
        path="/",
        secure=_cookie_is_secure(settings),
        httponly=True,
        samesite="lax",
    )


def _user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, email=user.email)
