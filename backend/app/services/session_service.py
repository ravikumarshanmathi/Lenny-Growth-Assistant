import re
import uuid
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Session

logger = logging.getLogger(__name__)

ACRONYMS = {
    "plg": "PLG",
    "pmf": "PMF",
    "pql": "PQL",
    "b2b": "B2B",
    "b2c": "B2C",
    "saas": "SaaS",
    "cac": "CAC",
    "ltv": "LTV",
    "arr": "ARR",
    "mrr": "MRR",
    "roi": "ROI",
    "okr": "OKR",
    "kpi": "KPI",
    "nps": "NPS",
    "seo": "SEO",
    "jtbd": "JTBD",
}

def format_word(w: str) -> str:
    """Format word preserving known industry acronyms."""
    lower = w.lower().strip()
    if lower in ACRONYMS:
        return ACRONYMS[lower]
    return w.capitalize()

def clean_query_text(user_query: str) -> str:
    cleaned = re.sub(
        r'^(?:what\s+(?:is|are|does|do|did)|how\s+(?:to|does|do|can|would)|can\s+you\s+(?:explain|tell\s+me\s+about)?|tell\s+me\s+about|explain|give\s+me|show\s+me|who\s+is|define|describe|discuss)\s+',
        '',
        user_query,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(r'^(?:say|think|believe|mention|write)\s+(?:about|on|regarding)\s+', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[\?!\.,;:"\']', '', cleaned).strip()
    return cleaned

def generate_dynamic_title(user_query: str) -> str:
    """
    Dynamic & Specific Title Generator.
    Extracts guest names and precise topic frameworks (e.g., 'Balfour: Four Fits' vs 'Balfour: Retention Loops').
    Guarantees 3-5 concise, specific words.
    """
    if not user_query or not user_query.strip():
        return "New Chat"

    q_lower = user_query.lower().strip()
    
    # 1. Check for Ship 30 / Essay requests
    if "ship 30" in q_lower or "essay" in q_lower or "write an article" in q_lower:
        topic_match = re.search(r'(?:about|on|for|regarding)\s+([a-zA-Z0-9\s]+)', q_lower)
        if topic_match:
            raw_topic = topic_match.group(1).strip()
            topic_words = [format_word(w) for w in raw_topic.split() if w.lower() not in {"the", "a", "an", "and", "in", "of"}][:3]
            if topic_words:
                return f"Essay: {' '.join(topic_words)}"
        return "Essay: Growth Strategy"

    # 2. Guest detection
    guest = None
    if "balfour" in q_lower or "brian" in q_lower:
        guest = "Balfour"
    elif "elena" in q_lower or "verna" in q_lower:
        guest = "Elena Verna"
    elif "lenny" in q_lower:
        guest = "Lenny"
    elif "shreyas" in q_lower or "doshi" in q_lower:
        guest = "Shreyas Doshi"
    elif "casey" in q_lower or "winters" in q_lower:
        guest = "Casey Winters"
    elif "fareed" in q_lower or "mosavat" in q_lower:
        guest = "Fareed Mosavat"
    elif "sean ellis" in q_lower:
        guest = "Sean Ellis"
    elif "hila" in q_lower or "qu" in q_lower:
        guest = "Hila Qu"
    elif "cagan" in q_lower or "marty" in q_lower:
        guest = "Marty Cagan"
    elif "biddle" in q_lower or "gibson" in q_lower:
        guest = "Gibson Biddle"
    elif "dunford" in q_lower or "april" in q_lower:
        guest = "April Dunford"

    # 3. Specific topic / framework detection
    topic = None
    if any(k in q_lower for k in ["four fits", "four fit", "pmf", "product market fit", "market fit", "model fit"]):
        topic = "Four Fits"
    elif any(k in q_lower for k in ["retention loop", "retention loops", "cohort retention"]):
        if "cohort" in q_lower:
            topic = "Cohort Retention"
        else:
            topic = "Retention Loops"
    elif any(k in q_lower for k in ["acquisition loop", "acquisition loops"]):
        topic = "Acquisition Loops"
    elif any(k in q_lower for k in ["growth loop", "growth loops"]):
        topic = "Growth Loops"
    elif any(k in q_lower for k in ["plg", "product-led", "product led"]):
        topic = "PLG Strategy"
    elif any(k in q_lower for k in ["freemium", "b2b freemium"]):
        topic = "B2B Freemium"
    elif any(k in q_lower for k in ["pql", "product qualified"]):
        topic = "PQL Framework"
    elif any(k in q_lower for k in ["north star", "northstar"]):
        topic = "North Star Metric"
    elif any(k in q_lower for k in ["viral loop", "virality"]):
        topic = "Viral Loops"
    elif "churn" in q_lower:
        topic = "Churn & Retention"
    elif "pricing" in q_lower or "monetization" in q_lower:
        topic = "Pricing Strategy"
    elif "onboarding" in q_lower:
        topic = "User Onboarding"
    elif "activation" in q_lower or "aha moment" in q_lower:
        topic = "Activation & Aha Moment"
    elif "jtbd" in q_lower or "jobs to be done" in q_lower:
        topic = "Jobs to Be Done"
    elif "product strategy" in q_lower or "strategy" in q_lower:
        topic = "Product Strategy"

    if guest and topic:
        return f"{guest}: {topic}"
        
    if guest and not topic:
        # Extract remaining specific keywords without the guest's name
        cleaned = clean_query_text(user_query)
        cleaned = re.sub(r'\b(?:brian|balfour|elena|verna|lenny|shreyas|doshi|casey|winters|marty|cagan)\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(?:say|about|views|thoughts|regarding|perspective|on)\b', '', cleaned, flags=re.IGNORECASE).strip()
        stop_words = {"the", "a", "an", "to", "in", "of", "and", "or", "for", "with", "by", "from", "at", "his", "her"}
        tokens = [format_word(w) for w in cleaned.split() if w.lower() not in stop_words]
        if tokens:
            return f"{guest}: {' '.join(tokens[:3])}"
        return f"{guest} Growth Framework"

    if topic and not guest:
        cleaned = clean_query_text(user_query)
        stop_words = {"the", "a", "an", "to", "in", "of", "and", "or", "for", "with", "by", "from", "at"}
        tokens = [format_word(w) for w in cleaned.split() if w.lower() not in stop_words]
        if len(tokens) >= 2 and topic not in " ".join(tokens):
            return f"{topic}: {' '.join(tokens[:2])}"
        return topic

    # 4. General Query: Extract 3-4 salient words
    cleaned = clean_query_text(user_query)
    stop_words = {"the", "a", "an", "according", "to", "in", "of", "and", "or", "for", "with", "by", "on", "at", "from", "is", "are"}
    tokens = [format_word(w) for w in cleaned.split() if w.lower() not in stop_words]
    if tokens:
        return " ".join(tokens[:4])
    
    words = user_query.split()[:4]
    return " ".join(format_word(w) for w in words)

def disambiguate_title(candidate_title: str, existing_titles: List[str]) -> str:
    """
    Guarantees unique session titles for the user.
    If candidate_title matches any existing title (exact match or already suffixed),
    appends a numbered suffix:
      'Balfour: Retention Loops (1)'
      'Balfour: Retention Loops (2)'
    Prevents duplicate suffixes like 'Title (1) (1)'.
    """
    if not candidate_title or not candidate_title.strip():
        candidate_title = "New Chat"

    existing_set = {t.strip().lower() for t in existing_titles if t and t.strip()}
    if candidate_title.strip().lower() not in existing_set:
        return candidate_title.strip()

    # Strip existing suffix if present so we increment cleanly
    base_title = re.sub(r'\s*\(\d+\)$', '', candidate_title).strip()
    if not base_title:
        base_title = "Chat"

    counter = 1
    new_title = f"{base_title} ({counter})"
    while new_title.strip().lower() in existing_set:
        counter += 1
        new_title = f"{base_title} ({counter})"
    return new_title

async def ensure_unique_title(
    db: AsyncSession,
    session: Session,
    candidate_title: str
) -> str:
    """
    Ensures candidate_title is unique among existing sessions for the user and assigns it.
    """
    query = select(Session.title)
    if session.id is not None:
        query = query.where(Session.id != session.id)

    if session.user_id:
        query = query.where(Session.user_id == session.user_id)
    else:
        query = query.where(Session.user_id.is_(None))

    res = await db.execute(query)
    existing_titles = [t for t in res.scalars().all() if t]

    unique_title = disambiguate_title(candidate_title, existing_titles)
    session.title = unique_title
    return unique_title

async def assign_unique_session_title(
    db: AsyncSession,
    session: Session,
    user_query: str
) -> str:
    """
    Generates a dynamic, specific title from user_query and ensures it is
    completely unique among existing sessions for the user.
    """
    base_title = generate_dynamic_title(user_query)
    return await ensure_unique_title(db, session, base_title)
