"""
Essay writer tool — generates Ship 30 for 30 style long-form content (~1,250 words).
Placeholder for Phase 2 implementation.
"""

from __future__ import annotations


async def generate_essay(topic: str, context_chunks: list[dict]) -> str:
    """
    Generate a ~1,250-word essay in the Ship 30 for 30 style,
    grounded in retrieved transcript chunks.

    Args:
        topic: Essay topic/thesis
        context_chunks: Retrieved transcript chunks with citation metadata

    Returns:
        Markdown-formatted essay with inline citations.

    TODO (Phase 2):
        - Construct essay prompt with context injection
        - Call LLM provider with essay-specific system prompt
        - Validate word count (1,000–1,500 range)
        - Validate citation count (≥ 3)
    """
    return ""
