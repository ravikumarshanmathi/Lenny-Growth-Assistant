"""
Chat schemas — Pydantic models for chat request/response validation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """A single source citation from the transcript corpus."""
    chunk_id: str = Field(..., description="UUID of the transcript chunk")
    episode_id: str = Field(..., description="Episode identifier")
    episode_title: str = Field(..., description="Episode title")
    guest_name: Optional[str] = Field(None, description="Guest speaker name")
    start_time: Optional[str] = Field(None, description="Approximate timestamp, e.g. '00:14:32'")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score")
    snippet: str = Field(..., description="Relevant text snippet from the chunk")


class ChatRequest(BaseModel):
    """Incoming chat message from the user."""
    session_id: Optional[str] = Field(None, description="Existing session UUID; null for new session")
    message: str = Field(..., min_length=1, max_length=4000, description="User's query or prompt")
    mode: str = Field(
        default="qa",
        description="Interaction mode: 'qa' for Q&A, 'essay' for Ship 30 for 30 generation",
    )


class ChatResponse(BaseModel):
    """Streamed or complete assistant response."""
    session_id: str
    message_id: str
    content: str
    citations: list[Citation] = Field(default_factory=list)
    model_used: str
    latency_ms: int
    has_artifact: bool = False
    timestamp: datetime
