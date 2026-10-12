import re
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rag_engine import (
    retrieve_grounded_context, search_local_transcripts_keyword, clean_retrieval_query,
    has_artifact_intent, ARTIFACT_SIMILARITY_THRESHOLD,
)
from app.services.llm_factory import llm_factory
from app.agents.skills.ship30_skill import generate_ship30_essay

logger = logging.getLogger(__name__)

class AgentRunner:
    """
    Agent orchestration engine combining intent classification, RAG retrieval, and specialized skills.
    """
    async def process_query(self, query: str, db_session: AsyncSession | None = None, provider_override: str | None = None) -> Dict[str, Any]:
        """
        Processes a user query and returns a structured payload containing the response, citations, artifacts, and metadata.
        """
        # 1. Retrieve RAG Context
        if db_session is not None:
            context_str, citations = await retrieve_grounded_context(query, db_session)
        else:
            # Database unavailable — use keyword fallback directly
            logger.info("DB session unavailable. Using local transcript keyword fallback for RAG.")
            clean_q = clean_retrieval_query(query)
            fallback_threshold = ARTIFACT_SIMILARITY_THRESHOLD if has_artifact_intent(query) else None
            keyword_matches = search_local_transcripts_keyword(clean_q, threshold=fallback_threshold)
            if keyword_matches:
                context_blocks = []
                citations = []
                for item, score in keyword_matches:
                    context_blocks.append(
                        f"[Source: {item['episode_title']} | File: {item['file_name']} | Guest: {item['guest_name']}]\n{item['content']}"
                    )
                    citations.append({
                        "episode_title": item["episode_title"],
                        "similarity_score": round(float(score), 2),
                        "metadata": {
                            "file_name": item["file_name"],
                            "chunk_order": 1,
                            "guest": item["guest_name"],
                            "chunk_content": item["content"]
                        }
                    })
                context_str = "\n\n---\n\n".join(context_blocks)
            else:
                context_str, citations = "", []
        
        # Enforce minimum similarity threshold cutoff
        if not context_str or not citations:
            return {
                "answer": "I am unable to find relevant insights on this topic in Lenny's Podcast transcripts.",
                "citations": [],
                "artifact": None,
                "active_provider": provider_override or "ollama",
                "fallback_triggered": False
            }

        # 2. Intent Classification
        # Using a keyword heuristic for fast routing (can be upgraded to LLM routing)
        intent = "qa"
        query_lower = query.lower()
        if "essay" in query_lower or "ship 30" in query_lower or "article" in query_lower or "post" in query_lower:
            intent = "essay"

        # 3. Execution Based on Intent
        artifact_payload = None
        
        if intent == "essay":
            if not citations:
                answer = "I'm sorry, but I couldn't find enough information in Lenny's Podcast transcripts to write an essay on this topic."
                active_provider = "system"
                fallback_triggered = False
            else:
                answer_content, active_provider, fallback_triggered = await generate_ship30_essay(query, context_str, provider_override)
                answer = "I have generated the requested Ship 30 for 30 essay. You can view it in the artifact panel."
                artifact_payload = {
                    "type": "markdown",
                    "title": f"Essay: {query[:30]}...",
                    "content": answer_content
                }
        else:
            # Standard Conversational QA
            # Detect if user is asking for code/HTML/CSS/UI generation
            code_gen_keywords = ["html", "css", "code", "visual", "layout", "mockup", "ui", "design",
                                 "landing page", "component", "webpage", "web page", "button", "form",
                                 "card", "hero", "navbar", "footer", "template", "scaffold", "snippet"]
            is_code_request = any(w in query_lower for w in code_gen_keywords)

            if is_code_request:
                system_prompt = (
                    "You are Lenny Assistant, an AI advisor strictly grounded in Lenny's Podcast transcripts.\n"
                    "- Answer user queries concisely and directly based ONLY on the provided transcript sources.\n"
                    "- Provide justified, high-density responses without fluff, repeating tokens, or hallucinating external facts.\n"
                    "- If the context does not contain enough relevant information to answer the prompt (or if the question is completely out of domain), state clearly: 'I am unable to find relevant insights on this topic in Lenny's Podcast transcripts.'\n"
                    "- When generating HTML/CSS code artifacts, write clean, self-contained HTML with embedded <style> tags tailored to the topic. Do not output placeholder comments or external stylesheet links.\n\n"
                    "### CRITICAL INSTRUCTIONS:\n"
                    "1. COMPLETE CODE ONLY: Output the ENTIRE, fully functioning HTML and CSS document. Do NOT use placeholder comments (e.g. '<!-- metrics here -->', '... // Additional styles'), ellipses ('...'), or tell the user to write code elsewhere. Every metric, header, card, and style rule must be fully written out.\n"
                    "2. MODERN STYLING: Include complete, polished CSS inside a `<style>` tag in the `<head>`. Use a modern dark theme with dark navy/slate background (#0f172a, #1e293b), crisp typography, clean card borders, and vibrant accents (#6366f1, #38bdf8).\n"
                    "3. PODCAST GROUNDING: Populate the cards with real metrics, frameworks, and insights from the retrieved context (e.g., Balfour's Four Fits, Elena Verna's retention loops, cohort metrics).\n"
                    "4. FORMAT: Wrap the entire HTML code inside a single ```html code block starting with `<!-- Artifact: [Title] -->`:\n"
                    "```html\n"
                    "<!-- Artifact: [Descriptive Title] -->\n"
                    "<!DOCTYPE html>\n"
                    "<html lang=\"en\">\n"
                    "<head>\n"
                    "  <meta charset=\"UTF-8\">\n"
                    "  <title>[Title]</title>\n"
                    "  <style>\n"
                    "    /* Complete CSS styles */\n"
                    "  </style>\n"
                    "</head>\n"
                    "<body>\n"
                    "  <!-- Complete, fully written markup -->\n"
                    "</body>\n"
                    "</html>\n"
                    "```\n"
                    "After the closing ```, write a 1-2 sentence summary of what was built.\n\n"
                    "5. FULL USER INTENT: The user's original query (provided as the user message) contains their complete request including formatting, layout, and content preferences. Honor all formatting and structural instructions precisely.\n\n"
                    "=== CONTEXT ===\n"
                    f"{context_str}\n"
                    "=== END CONTEXT ==="
                )
            else:
                system_prompt = (
                    "You are Lenny Assistant, an AI advisor strictly grounded in Lenny's Podcast transcripts.\n"
                    "- Answer user queries concisely and directly based ONLY on the provided transcript sources.\n"
                    "- Provide justified, high-density responses without fluff, repeating tokens, or hallucinating external facts.\n"
                    "- If the context does not contain enough relevant information to answer the prompt (or if the question is completely out of domain), state clearly: 'I am unable to find relevant insights on this topic in Lenny's Podcast transcripts.'\n"
                    "- When generating HTML/CSS code artifacts, write clean, self-contained HTML with embedded <style> tags tailored to the topic. Do not output placeholder comments or external stylesheet links.\n\n"
                    "### Mandatory Operational Rules:\n"
                    "1. Conciseness & Directness:\n"
                    "   - Deliver the key answer immediately in sentence 1. Avoid throat-clearing, introductory summaries, or meta-intros ('Based on transcripts...', 'According to her...', 'In this episode...').\n"
                    "   - Keep standard answers strictly punchy and under 180 words.\n\n"
                    "2. Accurate Framework Grounding:\n"
                    "   - Elena Verna (PLG): Define PLG strictly as the product being the primary acquisition, retention, and expansion engine ('The product is the channel, the product is the sales rep').\n"
                    "   - Brian Balfour (Growth & Retention): Define Retention Loops strictly as closed compounding systems (not customer survey feedback loops) and Product-Market Fit via the 'Four Fits' (Market-Product, Product-Channel, Channel-Model, Model-Market Fit).\n"
                    "   - Never generate generic definitions, placeholder episode numbers (e.g., 'Episode 1'), or fake CSS/HTML components when asked conceptual questions.\n\n"
                    "3. Source & Citation Rules:\n"
                    "   - Citations are rendered automatically by the UI using ingested file metadata (e.g. ep301_elena_verna.txt). Do NOT write a 'References:', 'Sources:', or citations list inside the answer text.\n\n"
                    "4. Output Format Handling:\n"
                    "   - The user's original query (provided as the user message) may include specific output format or structure requests (e.g., 'pricing table', 'essay', 'HTML component'). Honor these formatting instructions, using the retrieved context as the content source.\n\n"
                    "=== CONTEXT ===\n"
                    f"{context_str}\n"
                    "=== END CONTEXT ==="
                )
            
            if False: # Disabled early exit guardrail locally
                 answer = "I don't have enough information in the podcast transcripts to answer that question."
                 active_provider = "system"
                 fallback_triggered = False
            else:
                answer, active_provider, fallback_triggered = await llm_factory.generate_response(
                    provider_override=provider_override,
                    system_prompt=system_prompt,
                    user_query=query
                )

                # --- Post-processing: Degeneration / Repetition Detection ---
                # Detect and truncate repetitive token loops of non-whitespace characters (e.g., "0000000000...")
                # Note: Do NOT match whitespace/indentation spaces, which are normal in HTML/code
                repeat_match = re.search(r'([^\s]{3,20}?)\1{7,}', answer)
                if repeat_match:
                    answer = answer[:repeat_match.start()].strip()
                    if not answer:
                        answer = "I encountered an issue generating the response. Please try rephrasing your question."

                # Strip isolated garbage patterns (memory addresses, broken deep paths) outside of code blocks
                answer = re.sub(r'0x[0-9a-fA-F]{6,}', '', answer)

                # --- Artifact Extraction ---
                # Strategy 1: Detect ```html blocks containing <!-- Artifact: Title --> markers
                artifact_comment_pattern = re.compile(
                    r'```html\s*\n\s*<!--\s*Artifact:\s*(.+?)\s*-->\s*\n(.*?)```',
                    re.DOTALL
                )
                comment_match = artifact_comment_pattern.search(answer)
                
                if comment_match:
                    artifact_title = comment_match.group(1).strip()
                    html_content = comment_match.group(2).strip()
                    html_content = self._sanitize_html_artifact(html_content)
                    artifact_payload = {
                        "type": "html",
                        "title": artifact_title,
                        "content": html_content
                    }
                    before = answer[:comment_match.start()].strip()
                    after = answer[comment_match.end():].strip()
                    summary = f"I've rendered the **{artifact_title}** in the artifact viewer."
                    answer = f"{before}\n\n{summary}\n\n{after}".strip() if (before or after) else summary
                
                # Strategy 2: Plain ```html blocks (closed or unclosed) for code-generation requests
                elif "```html" in answer and is_code_request:
                    start_idx = answer.find("```html") + 7
                    end_idx = answer.find("```", start_idx)
                    
                    if end_idx != -1:
                        html_content = answer[start_idx:end_idx].strip()
                        before = answer[:start_idx-7].strip()
                        after = answer[end_idx+3:].strip()
                    else:
                        # Unclosed code block - take everything from start_idx to end
                        html_content = answer[start_idx:].strip()
                        before = answer[:start_idx-7].strip()
                        after = ""

                    # Extract title from <!-- Artifact: ... --> if present
                    inner_title_match = re.search(r'<!--\s*Artifact:\s*(.+?)\s*-->', html_content)
                    if inner_title_match:
                        artifact_title = inner_title_match.group(1).strip()
                    else:
                        artifact_title = "HTML Component Preview"
                    
                    html_content = self._sanitize_html_artifact(html_content)
                    artifact_payload = {
                        "type": "html",
                        "title": artifact_title,
                        "content": html_content
                    }
                    summary = f"I've rendered the requested HTML snippet in the artifact viewer."
                    answer = f"{before}\n\n{summary}\n\n{after}".strip() if (before or after) else summary
                
                # Strategy 3: Strip unwanted HTML from conceptual answers (non-code requests)
                elif "```html" in answer and not is_code_request:
                    answer = re.sub(r'```html\s*\n.*?```', '', answer, flags=re.DOTALL).strip()

                # 1. Clean up any delimiter tokens occasionally echoed by smaller models
                for delimiter in ["=== CONTEXT ===", "=== END CONTEXT ==="]:
                    if delimiter in answer:
                        answer = answer.split(delimiter)[0].strip()

                # 2. Clean up any trailing References / Sources / Citations sections
                ref_pattern = r'(?i)\n+\s*(?:###?\s*|\*\*|__)?\s*(?:references|sources|citations|related episodes|episode references)\b.*$'
                answer = re.sub(ref_pattern, '', answer, flags=re.DOTALL).strip()

                # 3. Strip meta-introductory phrases from beginning of sentence 1
                meta_patterns = [
                    r'^(?:based on the transcripts?,?\s*)',
                    r'^(?:based on transcripts?,?\s*)',
                    r'^(?:based on the podcast,?\s*)',
                    r'^(?:based on the context,?\s*)',
                    r'^(?:according to the transcripts?,?\s*)',
                    r'^(?:according to the podcast,?\s*)',
                    r'^(?:according to the context,?\s*)',
                    r'^(?:in the podcast transcripts?,?\s*)',
                    r'^(?:in this episode,?\s*)',
                    r'^(?:according to her,?\s*)',
                    r'^(?:according to him,?\s*)',
                ]
                for p in meta_patterns:
                    answer = re.sub(p, '', answer, flags=re.IGNORECASE).strip()
                if answer:
                    answer = answer[0].upper() + answer[1:]

                # 4. Strict Length Constraint: under ~180 words for standard QA (skip if artifact was generated)
                if not artifact_payload:
                    words = answer.split()
                    if len(words) > 200:
                        truncated = " ".join(words[:180])
                        last_period = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
                        if last_period > 50:
                            answer = truncated[:last_period+1]
                        else:
                            answer = truncated + "."

        return {
            "answer": answer.strip(),
            "citations": citations,
            "artifact": artifact_payload,
            "active_provider": active_provider,
            "fallback_triggered": fallback_triggered
        }

    def _sanitize_html_artifact(self, html_content: str) -> str:
        """
        Sanitize HTML artifact content to remove degenerate model output:
        memory addresses, broken file paths, garbage repeated strings, and broken src attributes.
        """
        if not html_content:
            return html_content

        # Remove memory address patterns (0x7f3a2b4c...)
        html_content = re.sub(r'0x[0-9a-fA-F]{6,}', '', html_content)

        # Remove Windows file paths (C:\Users\...\file.ext)
        html_content = re.sub(r'[A-Z]:\\[\w\\. ]+', '', html_content)

        # Remove deep Unix file paths (/usr/local/.../file.ext)
        html_content = re.sub(r'(?:/[\w.-]+){4,}\.\w{2,4}', '', html_content)

        # Fix broken src/href attributes pointing to local files or garbage
        html_content = re.sub(
            r'(src|href)\s*=\s*["\'](?:(?:\./|\.\./)[\w/.%-]+|[A-Z]:\\[^"\']+|/home/[^"\']+)["\']',
            r'\1=""',
            html_content
        )

        # Remove bare image filenames that aren't valid URLs
        html_content = re.sub(
            r'(?<=["\'])\s*[\w-]+\.(?:png|jpg|jpeg|gif|bmp|webp)\s*(?=["\'])',
            '',
            html_content
        )

        # Strip excessively long base64 data URIs (>500 chars is likely garbage)
        html_content = re.sub(
            r'data:image/[a-z]+;base64,[A-Za-z0-9+/=]{500,}',
            'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iIzMzMyIvPjwvc3ZnPg==',
            html_content
        )

        # Strip placeholder comment ellipses often left by smaller models
        html_content = re.sub(r'\.\.\.\s*//[^\n]*', '', html_content)

        # Ensure closing tags exist if opening tags are present
        if "<style" in html_content and "</style>" not in html_content:
            html_content += "\n    </style>"
        if "<body" in html_content and "</body>" not in html_content:
            html_content += "\n</body>"
        if "<html" in html_content and "</html>" not in html_content:
            html_content += "\n</html>"

        # Strip stray hex color tokens that lack property names inside CSS
        html_content = re.sub(r';\s*[0-9a-fA-F]{6}\s*;', ';', html_content)
        html_content = re.sub(r'{\s*[0-9a-fA-F]{6}\s*;', '{', html_content)

        # Collapse multiple blank lines into one
        html_content = re.sub(r'\n{3,}', '\n\n', html_content)

        return html_content.strip()

agent_runner = AgentRunner()
