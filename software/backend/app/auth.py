"""Keycloak bearer-token validation for user-facing API routes."""

from typing import Annotated, Any, cast

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient, decode
from jwt.exceptions import PyJWTError
from pydantic import BaseModel

from app.settings import Settings

bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    """Small identity projection derived from validated token claims."""

    sub: str
    username: str
    email: str | None = None


class TokenValidator:
    """Validate Keycloak access tokens against the configured JWKS endpoint."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.jwks_client = PyJWKClient(settings.keycloak_jwks_url)

    def validate(self, token: str) -> AuthenticatedUser:
        """Return selected claims from a valid RS256 access token."""

        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            claims: dict[str, Any] = decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.settings.keycloak_audience,
                issuer=self.settings.keycloak_issuer,
                options={"require": ["exp", "sub"]},
            )
            subject = claims["sub"]
            username = claims.get("preferred_username", subject)
            email = claims.get("email")
            if not isinstance(subject, str) or not isinstance(username, str):
                raise ValueError("Identity claims must be strings")
            if email is not None and not isinstance(email, str):
                raise ValueError("Email claim must be a string")
            return AuthenticatedUser(sub=subject, username=username, email=email)
        except (PyJWTError, ValueError, KeyError) as error:
            raise _unauthorised("Invalid or expired bearer token") from error


def require_identity(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> AuthenticatedUser:
    """Require and validate a bearer token for a FastAPI route."""

    if credentials is None:
        raise _unauthorised("Bearer token required")
    validator = cast(TokenValidator, request.app.state.token_validator)
    return validator.validate(credentials.credentials)


def _unauthorised(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
