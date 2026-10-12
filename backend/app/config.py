"""
Application configuration — resolved from environment variables via pydantic-settings.

Provider resolution order:
  1. ANTHROPIC_API_KEY set  → AnthropicProvider
  2. OPENAI_API_KEY set     → OpenAIProvider
  3. Fallback               → OllamaProvider (zero-cost default)
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderEnum(str, Enum):
    """Supported LLM provider backends."""
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class Settings(BaseSettings):
    """
    Centralized application settings.
    All values are read from environment variables (or .env file).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "The Lenny Growth Assistant"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "info"

    # --- Backend Server ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_reload: bool = True

    # --- LLM Provider ---
    llm_provider: LLMProviderEnum = LLMProviderEnum.OLLAMA

    # Ollama (local)
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "phi3:mini"

    # Anthropic (cloud)
    anthropic_api_key: Optional[str] = None

    # OpenAI (cloud)
    openai_api_key: Optional[str] = None

    # --- Database ---
    database_url: str = "postgresql+asyncpg://lenny:lenny_dev_password@127.0.0.1:5432/lenny_growth_assistant"
    postgres_user: str = "lenny"
    postgres_password: str = "lenny_dev_password"
    postgres_db: str = "lenny_growth_assistant"

    # --- RAG Pipeline ---
    chunk_size: int = 512
    chunk_overlap: int = 64
    retrieval_top_k: int = 10
    rerank_top_k: int = 5

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def resolved_provider(self) -> LLMProviderEnum:
        """
        Resolve the active LLM provider based on available API keys.
        Falls back to Ollama if no cloud keys are configured.
        """
        if self.llm_provider == LLMProviderEnum.ANTHROPIC and self.anthropic_api_key:
            return LLMProviderEnum.ANTHROPIC
        if self.llm_provider == LLMProviderEnum.OPENAI and self.openai_api_key:
            return LLMProviderEnum.OPENAI
        # Zero-cost fallback
        return LLMProviderEnum.OLLAMA


# Singleton instance — import this everywhere
settings = Settings()
