"""
Session schemas — Pydantic models for session management.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """Create a new chat session."""
    title: Optional[str] = Field(None, max_length=255, description="Optional session title")


class SessionResponse(BaseModel):
    """Session summary returned in list views."""
    id: str
    title: Optional[str]
    message_count: int = 0
    created_at: datetime
    updated_at: datetime


class SessionDetail(SessionResponse):
    """Full session with message history."""
    messages: list = Field(default_factory=list)  # List[ChatResponse] — circular import avoided
