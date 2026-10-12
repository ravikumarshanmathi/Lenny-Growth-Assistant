"""
Provider Factory — resolves the active LLM provider at startup (ADR-001).

Resolution order:
  1. If LLM_PROVIDER=anthropic and ANTHROPIC_API_KEY is set → AnthropicProvider
  2. If LLM_PROVIDER=openai and OPENAI_API_KEY is set → OpenAIProvider
  3. Fallback → OllamaProvider (zero-cost default)
"""

from __future__ import annotations

from app.agent.providers.base import LLMProvider
from app.config import LLMProviderEnum, settings


def create_provider() -> LLMProvider:
    """
    Factory function — instantiates the appropriate LLM provider
    based on environment configuration.

    Called once at application startup via the FastAPI lifespan.

    Returns:
        An instance of LLMProvider (Anthropic, OpenAI, or Ollama).

    Raises:
        ValueError: If a cloud provider is requested but its API key is missing.
    """
    resolved = settings.resolved_provider

    if resolved == LLMProviderEnum.ANTHROPIC:
        # Lazy import to avoid loading SDK when not needed
        from app.agent.providers.anthropic import AnthropicProvider
        return AnthropicProvider(api_key=settings.anthropic_api_key)

    if resolved == LLMProviderEnum.OPENAI:
        from app.agent.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(api_key=settings.openai_api_key)

    # Zero-cost fallback
    from app.agent.providers.ollama import OllamaProvider
    return OllamaProvider(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )
