import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.db.session import get_db
from app.db.models import Session, ChatMessage

router = APIRouter()

class SessionCreateRequest(BaseModel):
    title: str = "New Session"
    user_id: Optional[str] = None

class SessionResponse(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

from typing import List, Optional, Dict, Any

class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    citations: list
    provider_used: Optional[str]
    timestamp: datetime
    artifact: Optional[Dict[str, Any]] = None
    fallback_triggered: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

class SessionHistoryResponse(BaseModel):
    session: SessionResponse
    messages: List[ChatMessageResponse]

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(req: SessionCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create a new chat session."""
    try:
        new_session = Session(title=req.title, user_id=req.user_id)
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        return SessionResponse(
            id=str(new_session.id),
            title=new_session.title,
            user_id=new_session.user_id,
            created_at=new_session.created_at,
            updated_at=new_session.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: Cannot connect to PostgreSQL. Please ensure the database container is running (run: docker compose up db -d). Error: {str(e)}"
        )

@router.get("/", response_model=List[SessionResponse])
async def list_sessions(q: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """
    List all active sessions with timestamps.
    If 'q' is provided, filters sessions matching keywords in the title 
    OR in any chat message within the session.
    """
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        subquery = (
            select(ChatMessage.session_id)
            .where(ChatMessage.content.ilike(search_term))
            .distinct()
        )
        query = (
            select(Session)
            .where(
                (Session.title.ilike(search_term)) | (Session.id.in_(subquery))
            )
            .order_by(Session.updated_at.desc())
        )
    else:
        query = select(Session).order_by(Session.updated_at.desc())
        
    result = await db.execute(query)
    sessions = result.scalars().all()
    return [SessionResponse.model_validate(s) for s in sessions]

@router.get("/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve full conversation history for a session."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    session_res = await db.execute(select(Session).where(Session.id == session_uuid))
    session = session_res.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    from sqlalchemy.orm import selectinload
    
    messages_res = await db.execute(
        select(ChatMessage)
        .options(selectinload(ChatMessage.artifacts))
        .where(ChatMessage.session_id == session_uuid)
        .order_by(ChatMessage.timestamp.asc())
    )
    messages = messages_res.scalars().all()
    
    formatted_messages = []
    for m in messages:
        msg_dict = ChatMessageResponse.model_validate(m).model_dump()
        if m.artifacts:
            # Taking the first artifact if it exists
            art = m.artifacts[0]
            msg_dict["artifact"] = {
                "type": art.artifact_type,
                "title": art.artifact_type.capitalize() + " Artifact", # Simplified title
                "content": art.content
            }
        formatted_messages.append(msg_dict)
    
    return SessionHistoryResponse(
        session=SessionResponse.model_validate(session),
        messages=formatted_messages
    )

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a session, its messages, and any artifacts."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    session_res = await db.execute(select(Session).where(Session.id == session_uuid))
    session = session_res.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    from app.db.models import Artifact
    from sqlalchemy import delete
    
    msg_ids_res = await db.execute(select(ChatMessage.id).where(ChatMessage.session_id == session_uuid))
    msg_ids = msg_ids_res.scalars().all()
    if msg_ids:
        await db.execute(delete(Artifact).where(Artifact.message_id.in_(msg_ids)))
        await db.execute(delete(ChatMessage).where(ChatMessage.session_id == session_uuid))

    await db.delete(session)
    await db.commit()
    return None
