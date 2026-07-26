"""Health check endpoint router."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Service health status")
async def get_health_status():
    """Return 200 OK and status JSON."""
    return {"status": "ok", "service": "ClauseIQ-API"}
