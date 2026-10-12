import os
import logging
import httpx
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = (
    "You are Lenny Assistant, an AI advisor strictly grounded in Lenny's Podcast transcripts.\n"
    "- Answer user queries concisely and directly based ONLY on the provided transcript sources.\n"
    "- Provide justified, high-density responses without fluff, repeating tokens, or hallucinating external facts.\n"
    "- If the context does not contain enough relevant information to answer the prompt (or if the question is completely out of domain), state clearly: 'I am unable to find relevant insights on this topic in Lenny's Podcast transcripts.'\n"
    "- When generating HTML/CSS code artifacts, write clean, self-contained HTML with embedded <style> tags tailored to the topic. Do not output placeholder comments or external stylesheet links."
)
SYSTEM_PROMPT = DEFAULT_SYSTEM_PROMPT

class LLMProviderFactory:
    """
    Flexible LLM Provider Factory meeting Requirement 3.2.
    Supports Local Ollama (default), Anthropic Claude, and OpenAI.
    Implements graceful fallback logic.
    """
    def __init__(self):
        self.default_provider = "ollama"
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "phi3:mini")
        self.system_prompt = DEFAULT_SYSTEM_PROMPT

    def _generate_mock_framework_answer(self, user_query: str) -> str:
        q = user_query.lower()
        if any(k in q for k in ["balfour", "retention", "fit", "market fit"]):
            return (
                "Product-Market Fit is achieved and sustained strictly through the Four Fits framework: "
                "Market-Product Fit, Product-Channel Fit, Channel-Model Fit, and Model-Market Fit. "
                "Retention loops operate as closed compounding systems where cohort actions produce an output "
                "that directly re-engages existing users or acquires new ones, rather than linear feedback surveys."
            )
        return (
            "Product-Led Growth (PLG) defines a model where the product is the primary acquisition, retention, "
            "and expansion engine—the product is the channel, and the product is the sales rep. "
            "Sustainable growth is driven by self-serve loops and direct user value rather than isolated marketing hacks."
        )

    async def generate_response(
        self, 
        provider_override: str | None = None, 
        system_prompt: str | None = None, 
        user_query: str = ""
    ) -> Tuple[str, str, bool]:
        """
        Routes the query through the selected provider with graceful fallback.
        Returns: (response_text, active_provider, fallback_triggered)
        """
        prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        provider = provider_override or os.getenv("LLM_PROVIDER", self.default_provider)
        provider = provider.lower()
        
        fallback_triggered = False

        if provider == "anthropic":
            api_key = os.getenv("CLAUDE_API_KEY")
            if api_key and api_key != "sk-your-anthropic-api-key-here":
                try:
                    res = await self._call_anthropic(api_key, prompt, user_query)
                    return res, "anthropic", fallback_triggered
                except Exception as e:
                    logger.warning(f"Anthropic API call failed: {e}. Falling back to local Ollama execution.")
                    provider = "ollama"
                    fallback_triggered = True
            else:
                logger.info("Anthropic API key not configured or placeholder. Falling back to local Ollama.")
                provider = "ollama"
                fallback_triggered = True

        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key != "sk-your-openai-api-key-here":
                try:
                    res = await self._call_openai(api_key, prompt, user_query)
                    return res, "openai", fallback_triggered
                except Exception as e:
                    logger.warning(f"OpenAI API call failed: {e}. Falling back to local Ollama execution.")
                    provider = "ollama"
                    fallback_triggered = True
            else:
                logger.info("OpenAI API key not configured or placeholder. Falling back to local Ollama.")
                provider = "ollama"
                fallback_triggered = True

        # Fallback / Default: Local Ollama Execution
        try:
            response = await self._call_ollama(prompt, user_query)
            return response, "ollama", fallback_triggered
        except Exception as e:
            logger.error(f"Local Ollama execution failed: {e}")
            mock_response = (
                "**⚠️ System Notice:** I cannot answer your question because no LLM providers are configured. "
                "I tried to fall back to a local Ollama instance, but it is not running. "
                "To fix this, please run Ollama locally or provide an `OPENAI_API_KEY` or `CLAUDE_API_KEY` in your `.env` file."
            )
            return mock_response, "system", True

    async def _call_ollama(self, system_prompt: str, user_query: str) -> str:
        model = os.getenv("OLLAMA_MODEL", self.ollama_model)
        url = os.getenv("OLLAMA_BASE_URL", self.ollama_url)
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                "options": {
                    "num_predict": 1024,
                    "temperature": 0.1,
                    "repeat_penalty": 1.05,
                    "frequency_penalty": 0.0
                },
                "stream": False
            }
            res = await client.post(f"{url}/api/chat", json=payload, timeout=120.0)

            # If requested model is not found, attempt fallback to installed models from /api/tags
            if res.status_code == 404 or (res.status_code == 200 and "error" in res.json()):
                try:
                    tags_res = await client.get(f"{url}/api/tags", timeout=5.0)
                    if tags_res.status_code == 200:
                        installed_models = [m["name"] for m in tags_res.json().get("models", [])]
                        fallback_model = next((m for m in installed_models if "phi3" in m), installed_models[0] if installed_models else None)
                        if fallback_model and fallback_model != model:
                            logger.info(f"Ollama model '{model}' not found; falling back to installed model '{fallback_model}'")
                            payload["model"] = fallback_model
                            res = await client.post(f"{url}/api/chat", json=payload, timeout=120.0)
                except Exception as tag_err:
                    logger.warning(f"Failed to query Ollama installed models: {tag_err}")

            res.raise_for_status()
            data = res.json()
            if "error" in data:
                raise RuntimeError(data["error"])
            return data["message"]["content"]

    async def _call_anthropic(self, api_key: str, system_prompt: str, user_query: str) -> str:
        async with httpx.AsyncClient() as client:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1024,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": user_query}
                ]
            }
            res = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=60.0)
            res.raise_for_status()
            data = res.json()
            return data["content"][0]["text"]

    async def _call_openai(self, api_key: str, system_prompt: str, user_query: str) -> str:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "content-type": "application/json"
            }
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ]
            }
            res = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=60.0)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]

    async def generate_title(self, user_query: str, provider_override: Optional[str] = None) -> Optional[str]:
        """
        Generates a concise 3-5 word title unique to the exact prompt phrasing.
        """
        titling_prompt = (
            "Generate a concise 3 to 5 word title for a conversation starting with this query:\n"
            f"\"{user_query}\"\n"
            "Rules:\n"
            "- Strictly 3 to 5 words\n"
            "- Include specific keywords, frameworks, and guest names from the query\n"
            "- Do NOT include punctuation, quotes, or introductory text\n"
            "- Return ONLY the title"
        )
        try:
            provider = (provider_override or os.getenv("LLM_PROVIDER", self.default_provider)).lower()
            if provider == "anthropic" and os.getenv("CLAUDE_API_KEY"):
                res = await self._call_anthropic(os.getenv("CLAUDE_API_KEY"), "You are a concise titling assistant.", titling_prompt)
            elif provider == "openai" and os.getenv("OPENAI_API_KEY"):
                res = await self._call_openai(os.getenv("OPENAI_API_KEY"), "You are a concise titling assistant.", titling_prompt)
            else:
                res = await self._call_ollama("You are a concise titling assistant.", titling_prompt)
            
            clean_res = res.strip().strip('"\'')
            words = clean_res.split()
            if 2 <= len(words) <= 6:
                return " ".join(words[:5])
            return None
        except Exception as e:
            logger.warning(f"LLM titling failed: {e}")
            return None

llm_factory = LLMProviderFactory()

