"""
Session routes — CRUD operations for chat sessions.
Placeholder for Phase 2 implementation.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/sessions")
async def list_sessions():
    """GET /api/sessions — returns all chat sessions, ordered by updated_at desc."""
    return {"sessions": [], "status": "placeholder"}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """GET /api/sessions/{id} — returns session detail with message history."""
    return {"session_id": session_id, "messages": [], "status": "placeholder"}


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """DELETE /api/sessions/{id} — soft-deletes a session and its messages."""
    return {"session_id": session_id, "deleted": False, "status": "placeholder"}
