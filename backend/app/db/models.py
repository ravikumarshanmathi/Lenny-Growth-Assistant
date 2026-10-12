"""
Database models — SQLAlchemy ORM definitions for PostgreSQL.
Implements the schema from Phase 0 ADR-002, updated for Phase 3.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    JSON
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


class Session(Base):
    """Chat session — groups related messages."""
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=True)
    user_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    metadata_ = Column("metadata", JSONB, default=dict)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.timestamp")

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, title={self.title!r})>"


class ChatMessage(Base):
    """Individual chat message within a session."""
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    citations = Column(JSONB, default=list)
    provider_used = Column(String(100), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="ck_chat_message_role"),
        Index("idx_chat_messages_session", "session_id", "timestamp"),
    )

    # Relationships
    session = relationship("Session", back_populates="messages")
    artifacts = relationship("Artifact", back_populates="message", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, role={self.role!r})>"


class Artifact(Base):
    """Rendered artifact (Markdown/HTML/CSS) attached to a message."""
    __tablename__ = "artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    artifact_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    sanitized = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("artifact_type IN ('markdown', 'html', 'css')", name="ck_artifact_type"),
    )

    # Relationships
    message = relationship("ChatMessage", back_populates="artifacts")

    def __repr__(self) -> str:
        return f"<Artifact(id={self.id}, type={self.artifact_type!r})>"


class TranscriptChunk(Base):
    """
    RAG corpus — chunked and embedded transcript segments.
    Updated for Phase 2 implementation.
    """
    __tablename__ = "transcript_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_title = Column(String(255), nullable=False)
    guest_name = Column(String(255), nullable=True)
    source_url = Column(String(512), nullable=True)
    chunk_content = Column(Text, nullable=False)
    chunk_index = Column(String, nullable=False)
    # Embedding using sentence-transformers/all-MiniLM-L6-v2, which has 384 dimensions
    embedding = Column(JSON)  # Changed from Vector(384) to JSON for local native Postgres compatibility
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<TranscriptChunk(id={self.id}, episode={self.episode_title!r}, chunk={self.chunk_index})>"
