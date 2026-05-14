import asyncio
import logging

from fastapi import APIRouter

from app.config.settings import get_settings
from app.services.dependency import observed_dependency_call

router = APIRouter(prefix="/api/v1/simulate", tags=["simulation"])
logger = logging.getLogger("opsight.simulation")


@router.get("/latency")
async def simulate_latency() -> dict[str, str]:
    settings = get_settings()
    logger.warning("latency simulation triggered", extra={"scenario": "high_latency"})
    await asyncio.sleep(settings.latency_simulation_ms / 1000)
    await observed_dependency_call(settings, operation="slow-authorize", latency_multiplier=8)
    return {"status": "degraded", "scenario": "high_latency"}


@router.get("/error")
async def simulate_error() -> dict[str, str]:
    logger.error("error simulation triggered", extra={"scenario": "increased_500s"})
    raise RuntimeError("simulated application exception")


@router.get("/dependency-failure")
async def simulate_dependency_failure() -> dict[str, str]:
    logger.warning("dependency failure simulation triggered", extra={"scenario": "dependency_degradation"})
    await observed_dependency_call(get_settings(), operation="authorize", force_failure=True)
    return {"status": "unreachable"}
