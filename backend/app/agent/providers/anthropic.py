"""
Anthropic Provider — Claude API integration (ADR-001).
Placeholder for Phase 2 implementation.
"""

from __future__ import annotations

from typing import AsyncIterator, Optional

from app.agent.providers.base import GenerationResult, LLMProvider


class AnthropicProvider(LLMProvider):
    """LLM provider backed by Anthropic's Claude API."""

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key
        # TODO (Phase 2): Initialize anthropic.AsyncAnthropic client

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def model_name(self) -> str:
        return "claude-sonnet-4-20250514"

    async def generate(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> GenerationResult:
        # TODO (Phase 2): Implement Anthropic Messages API call
        raise NotImplementedError("AnthropicProvider.generate() — implement in Phase 2")

    async def stream(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        # TODO (Phase 2): Implement streaming with anthropic.AsyncAnthropic
        raise NotImplementedError("AnthropicProvider.stream() — implement in Phase 2")
        yield  # type: ignore  # Makes this a valid async generator

    async def embed(self, text: str) -> list[float]:
        # Anthropic doesn't have an embeddings API — use OpenAI's
        raise NotImplementedError(
            "AnthropicProvider.embed() — delegate to OpenAI or use sentence-transformers"
        )
