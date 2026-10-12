"""
Preprocessor — transcript cleaning and normalization.
Placeholder for Phase 2 implementation.
"""

from __future__ import annotations


def preprocess_transcript(raw_text: str, episode_id: str) -> dict:
    """
    Clean and normalize a raw transcript.

    Processing steps:
      1. Strip HTML/formatting artifacts
      2. Normalize whitespace and line breaks
      3. Tag speaker diarization segments (if present)
      4. Compute quality score

    Args:
        raw_text: Raw transcript content
        episode_id: Episode identifier for metadata

    Returns:
        Dict with cleaned text, metadata, and quality score.
    """
    # TODO (Phase 2): Implement full preprocessing pipeline
    return {
        "text": raw_text.strip(),
        "episode_id": episode_id,
        "quality_score": 1.0,
    }
