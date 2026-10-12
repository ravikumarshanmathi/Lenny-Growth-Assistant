"""
Retrieval tool — vector search over the transcript corpus.
Placeholder for Phase 2 implementation.
"""

from __future__ import annotations


async def search_transcripts(query: str, top_k: int = 10) -> list[dict]:
    """
    Search the transcript corpus for chunks relevant to the query.

    Args:
        query: User's natural language query
        top_k: Number of results to return

    Returns:
        List of dicts with chunk content, citations, and relevance scores.

    TODO (Phase 2):
        - Embed the query using the active provider
        - pgvector cosine similarity search
        - Optional cross-encoder re-ranking
        - Return citation metadata
    """
    return []
