import re
import uuid
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.db.session import get_db
from app.db.models import Session, ChatMessage, Artifact
from app.agents.agent_runner import agent_runner
from app.services.session_service import assign_unique_session_title, generate_dynamic_title

# Backward compatibility alias
generate_concise_title = generate_dynamic_title

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    message: str
    provider_override: Optional[str] = None

class Citation(BaseModel):
    episode_title: str
    similarity_score: float
    metadata: Dict[str, Any]

class ArtifactResponse(BaseModel):
    type: str
    title: str
    content: str

class ChatResponse(BaseModel):
    session_id: str
    session_title: Optional[str] = None
    answer: str
    citations: List[Citation]
    artifact: Optional[ArtifactResponse] = None
    active_provider: str
    fallback_triggered: bool

@router.post("/", response_model=ChatResponse)
async def process_chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Process user queries via AgentRunner.
    Persists session messages, citations, generated artifacts, and model provider.
    Gracefully degrades when the database is unavailable.
    """
    try:
        session_uuid = uuid.UUID(req.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    # --- Phase 1: DB-dependent operations (wrapped for resilience) ---
    db_available = True
    session = None
    assigned_title = None

    try:
        # Verify session exists
        session_res = await db.execute(select(Session).where(Session.id == session_uuid))
        session = session_res.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Dynamically update session title
        assigned_title = session.title
        if session.title in ("New Session", "New Chat", None) or (session.title and session.title.startswith("New")):
            assigned_title = await assign_unique_session_title(db, session, req.message)

        # Persist user message
        user_msg = ChatMessage(
            session_id=session_uuid,
            role="user",
            content=req.message,
        )
        db.add(user_msg)
        await db.commit()

    except HTTPException:
        raise  # Re-raise explicit HTTP errors (like 404)
    except Exception as e:
        logger.warning(f"Database unavailable during chat — operating in degraded mode: {e}")
        db_available = False
        assigned_title = generate_dynamic_title(req.message)

    # --- Phase 2: Run Agent Engine (works with or without DB) ---
    try:
        result = await agent_runner.process_query(
            query=req.message, 
            db_session=db if db_available else None, 
            provider_override=req.provider_override
        )
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(status_code=503, detail="Agent execution failed. Providers might be unreachable.")

    # --- Phase 3: Persist response (best-effort when DB is available) ---
    if db_available:
        try:
            assistant_msg = ChatMessage(
                session_id=session_uuid,
                role="assistant",
                content=result["answer"],
                citations=result["citations"],
                provider_used=result["active_provider"]
            )
            db.add(assistant_msg)
            await db.flush()

            # Persist Artifact (if generated)
            artifact_data = result.get("artifact")
            if artifact_data:
                db_artifact = Artifact(
                    message_id=assistant_msg.id,
                    artifact_type=artifact_data["type"],
                    content=artifact_data["content"],
                    sanitized=False
                )
                db.add(db_artifact)

            # Update session timestamp
            if session:
                session.updated_at = datetime.utcnow()
            await db.commit()
        except Exception as e:
            logger.warning(f"Failed to persist assistant response to DB: {e}")

    return ChatResponse(
        session_id=str(session_uuid),
        session_title=assigned_title,
        answer=result["answer"],
        citations=result["citations"],
        artifact=result.get("artifact"),
        active_provider=result["active_provider"],
        fallback_triggered=result["fallback_triggered"]
    )
