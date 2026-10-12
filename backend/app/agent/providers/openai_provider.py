"""
OpenAI Provider — GPT API integration (ADR-001).
Placeholder for Phase 2 implementation.
"""

from __future__ import annotations

from typing import AsyncIterator, Optional

from app.agent.providers.base import GenerationResult, LLMProvider


class OpenAIProvider(LLMProvider):
    """LLM provider backed by OpenAI's API."""

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key
        # TODO (Phase 2): Initialize openai.AsyncOpenAI client

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return "gpt-4o"

    async def generate(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> GenerationResult:
        # TODO (Phase 2): Implement OpenAI Chat Completions API call
        raise NotImplementedError("OpenAIProvider.generate() — implement in Phase 2")

    async def stream(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        # TODO (Phase 2): Implement streaming with openai.AsyncOpenAI
        raise NotImplementedError("OpenAIProvider.stream() — implement in Phase 2")
        yield  # type: ignore  # Makes this a valid async generator

    async def embed(self, text: str) -> list[float]:
        # TODO (Phase 2): Implement text-embedding-3-small
        raise NotImplementedError("OpenAIProvider.embed() — implement in Phase 2")
