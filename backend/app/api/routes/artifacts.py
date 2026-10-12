"""
Artifact routes — retrieval and creation of rendered artifacts.
Placeholder for Phase 2 implementation.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str):
    """GET /api/artifacts/{id} — returns a sanitized artifact by ID."""
    return {"artifact_id": artifact_id, "content": None, "status": "placeholder"}


@router.post("/artifacts")
async def create_artifact():
    """
    POST /api/artifacts — stores a new artifact (server-side sanitized).

    TODO (Phase 2):
      - Accept ArtifactCreate schema
      - Sanitize HTML via bleach before persistence
      - Store in artifacts table
    """
    return {"message": "Artifact creation — not yet implemented", "status": "placeholder"}
