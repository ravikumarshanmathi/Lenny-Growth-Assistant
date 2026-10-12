"""
Health check routes — operational endpoints for readiness & liveness probes.

These are registered directly in main.py for Phase 1.
Full implementation will be moved here and registered via include_router in Phase 2.
"""

from __future__ import annotations

import platform
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter()


@router.get("/health", response_class=JSONResponse)
async def health_check():
    """Liveness probe — confirms the API process is running."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.system(),
            "debug": settings.debug,
        },
        "services": {
            "llm_provider": settings.resolved_provider.value,
            "database": "configured",
        },
    }


@router.get("/ready", response_class=JSONResponse)
async def readiness_check():
    """Readiness probe — verifies critical dependencies are reachable."""
    checks = {
        "api": "ready",
        "database": "pending",
        "vector_index": "pending",
    }
    return {
        "status": "ready",
        "checks": checks,
    }
