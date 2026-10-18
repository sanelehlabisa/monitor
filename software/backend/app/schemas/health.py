"""Stable process-health response validation."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Stable process-health response returned to local tooling."""

    status: Literal["ok"] = "ok"
    service: str
    version: str
    environment: str
