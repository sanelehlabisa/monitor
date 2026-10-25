"""FastAPI routes and reusable dependency for human authentication."""

from dataclasses import dataclass
import os

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.database import connect_database
from app.modules.email_delivery import EmailDeliveryError, deliver_login_code
from app.modules.otp import (
    OtpRateLimitError,
    OtpVerificationError,
    User,
    get_otp_secret,
    verify_otp,
)
from app.modules.sessions import (
    SESSION_TTL,
    CreatedSession,
    SessionAuthenticationError,
    authenticate_session,
    create_session,
    revoke_session,
)
from app.schemas.auth import (
    AcceptedResponse,
    EmailRequest,
    UserResponse,
    VerifyOtpRequest,
)

COOKIE_NAME = "monitor_session"
REQUEST_ACCEPTED_MESSAGE = (
    "If the address can receive email, a sign-in code has been sent."
)

router = APIRouter(prefix="/api")


@dataclass(frozen=True)
class AuthenticatedUser:
    """Session-authenticated user plus database-derived access level."""

    user: User
    is_admin: bool


@router.post(
    "/auth/request-otp",
    response_model=AcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def request_otp(payload: EmailRequest, request: Request) -> AcceptedResponse:
    """Request a code without exposing policy or delivery outcomes."""

    try:
        with connect_database() as connection:
            deliver_login_code(connection, payload.email)
    except (OtpRateLimitError, EmailDeliveryError):
        pass
    return AcceptedResponse(message=REQUEST_ACCEPTED_MESSAGE)


@router.post("/auth/verify-otp", response_model=UserResponse)
def verify_code(
    payload: VerifyOtpRequest, request: Request, response: Response
) -> UserResponse:
    """Verify the newest code and establish an opaque cookie session."""

    try:
        with connect_database() as connection:
            user = verify_otp(
                connection,
                payload.email,
                payload.code,
                get_otp_secret(),
            )
            session = create_session(connection, user.id)
    except OtpVerificationError as error:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid or expired code"
        ) from error

    _set_session_cookie(response, session)
    return _user_response(user)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response) -> None:
    """Revoke only the presented session and always clear its cookie."""

    token = request.cookies.get(COOKIE_NAME)
    if token:
        try:
            with connect_database() as connection:
                revoke_session(connection, token)
        except SessionAuthenticationError:
            pass
    response.delete_cookie(
        COOKIE_NAME,
        path="/",
        secure=_cookie_is_secure(),
        httponly=True,
        samesite="lax",
    )


@router.get("/me", response_model=UserResponse)
def current_user(request: Request) -> UserResponse:
    """Return the user authenticated by the opaque session cookie."""

    authenticated = require_authenticated_user(request)
    return UserResponse(
        id=authenticated.user.id,
        email=authenticated.user.email,
        is_admin=authenticated.is_admin,
    )


def require_authenticated_user(request: Request) -> AuthenticatedUser:
    """Resolve the session cookie or return one generic authentication error."""

    token = request.cookies.get(COOKIE_NAME)
    try:
        if not token:
            raise SessionAuthenticationError("Session is unavailable")
        with connect_database() as connection:
            user = authenticate_session(connection, token)
    except SessionAuthenticationError as error:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Authentication required"
        ) from error
    return AuthenticatedUser(user=user, is_admin=user.type == "admin")


def _cookie_is_secure() -> bool:
    return os.environ["MONITOR_ENVIRONMENT"] != "development"


def _set_session_cookie(
    response: Response, session: CreatedSession
) -> None:
    response.set_cookie(
        COOKIE_NAME,
        session.token,
        max_age=int(SESSION_TTL.total_seconds()),
        expires=session.expires_at,
        path="/",
        secure=_cookie_is_secure(),
        httponly=True,
        samesite="lax",
    )


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id, email=user.email, is_admin=user.type == "admin"
    )
