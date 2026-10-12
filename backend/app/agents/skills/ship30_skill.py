import logging
from typing import Tuple
from app.services.llm_factory import llm_factory

logger = logging.getLogger(__name__)

async def generate_ship30_essay(topic: str, context_str: str, provider_override: str | None = None) -> Tuple[str, str, bool]:
    """
    Generates a ~1,250-word essay following Ship 30 for 30 principles based on transcript context.
    Returns: (essay_content, active_provider, fallback_triggered)
    """
    system_prompt = (
        "You are a master essayist following the 'Ship 30 for 30' writing principles. "
        "Your task is to write an essay of approximately 1,250 words based STRICTLY on the provided transcript context.\n\n"
        "### Writing Guidelines:\n"
        "1. **Strong Hook:** Open with a compelling problem or insight that immediately grabs attention.\n"
        "2. **Skimmability:** Use clear headings, bullet points, and selective bolding to make the text easy to scan.\n"
        "3. **Actionable Takeaways:** Provide a specific, actionable framework or set of steps the reader can apply.\n"
        "4. **No Fabrication:** All claims MUST be grounded in the retrieved transcript context. Do not invent information.\n"
        "5. **Source Citations:** Inline cite your sources using the episode titles provided in the context.\n\n"
        "If the context is completely insufficient to write an essay on the topic, state clearly that you lack the necessary "
        "transcript information to fulfill the request.\n\n"
        "=== CONTEXT ===\n"
        f"{context_str}\n"
        "=== END CONTEXT ==="
    )

    try:
        response, active_provider, fallback_triggered = await llm_factory.generate_response(
            provider_override=provider_override,
            system_prompt=system_prompt,
            user_query=f"Write a Ship 30 for 30 style essay about: {topic}"
        )
        return response, active_provider, fallback_triggered
    except Exception as e:
        logger.error(f"Failed to generate Ship 30 essay: {e}")
        raise
