"""
Artifact schemas — Pydantic models for rendered artifact management.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    """Supported artifact content types."""
    MARKDOWN = "markdown"
    HTML = "html"
    CSS = "css"


class ArtifactCreate(BaseModel):
    """Request to store a new artifact."""
    message_id: str = Field(..., description="UUID of the parent message")
    artifact_type: ArtifactType
    content: str = Field(..., min_length=1, description="Raw artifact content (sanitized server-side)")


class ArtifactResponse(BaseModel):
    """Artifact returned to the client (post-sanitization)."""
    id: str
    message_id: str
    artifact_type: ArtifactType
    content: str
    sanitized: bool = True
    created_at: datetime
