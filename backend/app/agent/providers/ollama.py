"""
Ollama Provider — local LLM inference via Ollama's OpenAI-compatible API.

This is the zero-cost default provider (ADR-001).
Requires Ollama running at OLLAMA_BASE_URL (default: http://ollama:11434).
"""

from __future__ import annotations

from typing import AsyncIterator, Optional

import httpx

from app.agent.providers.base import GenerationResult, LLMProvider


class OllamaProvider(LLMProvider):
    """
    LLM provider backed by a local Ollama instance.

    Uses the /api/chat endpoint for generation and
    /api/embeddings endpoint for text embeddings.
    """

    def __init__(self, base_url: str = "http://ollama:11434", model: str = "llama3:8b"):
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=120.0)

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> GenerationResult:
        """Generate a complete response using Ollama's /api/chat endpoint."""
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        response = await self._client.post(
            "/api/chat",
            json={
                "model": self._model,
                "messages": payload_messages,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                },
            },
        )
        response.raise_for_status()
        data = response.json()

        return GenerationResult(
            content=data["message"]["content"],
            model=self._model,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
            },
            finish_reason="stop",
        )

    async def stream(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream response tokens from Ollama for SSE delivery."""
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        async with self._client.stream(
            "POST",
            "/api/chat",
            json={
                "model": self._model,
                "messages": payload_messages,
                "stream": True,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                },
            },
        ) as response:
            response.raise_for_status()
            import json
            async for line in response.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    if not chunk.get("done", False):
                        yield chunk["message"]["content"]

    async def embed(self, text: str) -> list[float]:
        """Generate an embedding using Ollama's /api/embeddings endpoint."""
        response = await self._client.post(
            "/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": text,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["embedding"]
