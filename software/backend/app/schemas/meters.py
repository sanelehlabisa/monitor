"""Request and response validation for named meter profiles."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.modules.meters import normalize_meter_name


class MeterNameRequest(BaseModel):
    """The only user-entered value required by a V1 meter profile."""

    name: str = Field(min_length=1, max_length=80)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return normalize_meter_name(value)


class MeterResponse(BaseModel):
    """Compatible meter representation; owner_email is creator metadata only."""

    id: UUID
    name: str
    owner_email: str
    created_at: datetime
    updated_at: datetime


class MemberResponse(BaseModel):
    """A meter member, without global role or account-existence details."""

    user_id: int
    email: str
