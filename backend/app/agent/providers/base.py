"""
LLM Provider — Abstract Base Class (ADR-001).

All concrete providers (Anthropic, OpenAI, Ollama) implement this interface.
The ProviderFactory resolves the active provider at application startup.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional


@dataclass
class GenerationResult:
    """Structured result from an LLM generation call."""
    content: str
    model: str
    usage: dict = field(default_factory=dict)       # token counts
    finish_reason: Optional[str] = None


class LLMProvider(ABC):
    """
    Abstract interface for LLM providers.

    All providers must implement:
      - generate(): single-shot completion
      - stream(): streaming completion (SSE-compatible)
      - embed(): text → vector embedding
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier (e.g., 'anthropic', 'ollama')."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Active model identifier (e.g., 'claude-sonnet-4-20250514', 'llama3:8b')."""
        ...

    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> GenerationResult:
        """
        Generate a complete response (non-streaming).

        Args:
            messages: Conversation history in OpenAI-style format
                      [{"role": "user", "content": "..."}]
            system_prompt: Optional system instruction
            max_tokens: Maximum output tokens
            temperature: Sampling temperature

        Returns:
            GenerationResult with content, model name, and token usage
        """
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Stream response tokens (for SSE delivery to frontend).

        Yields:
            Individual text chunks as they are generated
        """
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """
        Generate an embedding vector for the given text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector.
            Dimension depends on the provider's embedding model.
        """
        ...
