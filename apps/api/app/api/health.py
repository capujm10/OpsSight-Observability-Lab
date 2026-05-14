from fastapi import APIRouter

from app.config.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def ready() -> dict[str, str]:
    settings = get_settings()
    if not settings.readiness_dependency_enabled:
        return {"status": "degraded", "dependency": "disabled"}
    return {"status": "ready"}
