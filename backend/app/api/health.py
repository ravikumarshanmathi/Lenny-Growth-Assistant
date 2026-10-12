import os
import httpx
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def check_health(db: AsyncSession = Depends(get_db)):
    """
    Diagnostic health check returning status of Database connection, 
    Ollama service availability, and configured Cloud API keys status.
    """
    health_status = {
        "status": "ok",
        "database": "disconnected",
        "ollama": "disconnected",
        "api_keys": {
            "anthropic": "configured" if os.getenv("CLAUDE_API_KEY") else "missing",
            "openai": "configured" if os.getenv("OPENAI_API_KEY") else "missing"
        }
    }
    
    # Check DB
    try:
        await db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["status"] = "degraded"
        
    # Check Ollama
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{ollama_url}/api/tags", timeout=5.0)
            if res.status_code == 200:
                health_status["ollama"] = "connected"
            else:
                health_status["ollama"] = f"error: {res.status_code}"
                health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        health_status["status"] = "degraded"
        
    return health_status
