"""
Agent orchestrator — main entry point for the retrieve → generate → cite pipeline.
Placeholder for Phase 2 implementation.
"""

from __future__ import annotations

from app.agent.providers.base import LLMProvider


class AgentOrchestrator:
    """
    Orchestrates the full conversational pipeline:
      1. Receive user message
      2. Classify intent (Q&A vs. essay)
      3. Retrieve relevant transcript chunks (RAG)
      4. Generate response with source citations
      5. Optionally create artifact (HTML/CSS/Markdown)
      6. Stream response to frontend via SSE

    TODO (Phase 2):
        - Implement full pipeline
        - Wire up retrieval, essay writer, and artifact tools
        - Add citation validation
        - SSE streaming integration
    """

    def __init__(self, provider: LLMProvider):
        self._provider = provider

    async def process_message(self, session_id: str, message: str, mode: str = "qa") -> dict:
        """
        Process a user message through the full pipeline.

        Args:
            session_id: Active session UUID
            message: User's query or prompt
            mode: 'qa' for Q&A, 'essay' for Ship 30 for 30 generation

        Returns:
            Dict with response content, citations, and optional artifact.
        """
        return {
            "content": f"[{self._provider.provider_name}] Orchestrator placeholder — not yet implemented.",
            "citations": [],
            "artifact": None,
            "model": self._provider.model_name,
        }
