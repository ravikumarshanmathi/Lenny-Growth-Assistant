import pytest
import os
from unittest.mock import patch
from app.services.llm_factory import llm_factory

@pytest.mark.asyncio
async def test_llm_factory_graceful_fallback():
    """
    Test provider switching and verify that selecting Cloud providers without 
    valid API keys gracefully triggers the local Ollama fallback.
    """
    with patch.dict(os.environ, {"LLM_PROVIDER": "anthropic", "CLAUDE_API_KEY": ""}), \
         patch.object(llm_factory, '_call_ollama', return_value="Ollama local fallback response") as mock_ollama:
        
        response, active_provider, fallback = await llm_factory.generate_response(None, "System setup", "Query")
        
        # Assertions
        assert active_provider == "ollama"
        assert fallback is True
        assert response == "Ollama local fallback response"
        mock_ollama.assert_called_once()

def test_system_prompt_grounding():
    """Verify that the system prompt strictly grounds Lenny Assistant."""
    from app.services.llm_factory import DEFAULT_SYSTEM_PROMPT
    assert "You are Lenny Assistant, an AI advisor strictly grounded in Lenny's Podcast transcripts." in DEFAULT_SYSTEM_PROMPT
    assert "I am unable to find relevant insights on this topic in Lenny's Podcast transcripts." in DEFAULT_SYSTEM_PROMPT
    assert "clean, self-contained HTML with embedded <style> tags" in DEFAULT_SYSTEM_PROMPT
