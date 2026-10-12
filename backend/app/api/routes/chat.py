"""
Chat routes — handles conversational Q&A and essay generation requests.
Placeholder for Phase 2 implementation.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("/chat")
async def chat():
    """
    POST /api/chat
    Accepts a user message, runs the RAG retrieval → LLM generation pipeline,
    and streams the response via SSE with citation metadata.

    TODO (Phase 2):
      - Accept ChatRequest schema
      - Integrate agent orchestrator
      - SSE streaming response
      - Citation metadata injection
    """
    return {"message": "Chat endpoint — not yet implemented", "status": "placeholder"}
