"""
Chunker — splits transcript text into overlapping chunks for embedding.
Placeholder for Phase 2 implementation.

Strategy (ADR-002):
  - Chunk size: 512 tokens
  - Overlap: 64 tokens (12.5%)
  - Respects paragraph boundaries where possible
"""

from __future__ import annotations

from app.config import settings


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Raw transcript text
        chunk_size: Token count per chunk (default from settings)
        overlap: Token overlap between consecutive chunks

    Returns:
        List of text chunks
    """
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    # TODO (Phase 2): Implement token-aware chunking with paragraph boundaries
    return [text]  # Placeholder — returns full text as single chunk
