"""Liveness and readiness endpoints, served at the root (NOT under /api): the kubelet probes them."""

from fastapi import APIRouter
from sqlalchemy import text

from app.deps import DbSession

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness: the process is up. Keep it cheap and dependency-free."""
    return {"status": "ok"}


@router.get("/ready")
async def ready(db: DbSession) -> dict[str, str]:
    """Readiness: the database answers."""
    await db.execute(text("SELECT 1"))
    return {"status": "ready"}
