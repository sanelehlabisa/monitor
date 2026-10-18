"""Request and response validation for email authentication."""

from pydantic import BaseModel, Field, field_validator

from app.modules.otp import normalize_email

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+$"


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
    is_admin: bool
