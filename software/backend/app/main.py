"""Minimal FastAPI application used by the development stack."""

from fastapi import FastAPI

app = FastAPI(title="Monitor API", version="0.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Report whether the placeholder API process is running."""
    return {"status": "ok"}
