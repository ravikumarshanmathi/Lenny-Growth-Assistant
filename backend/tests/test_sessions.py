import pytest
import uuid
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.db.session import get_db

@pytest.mark.asyncio
async def test_create_session():
    """Test creation of chat sessions in PostgreSQL via the API."""
    transport = ASGITransport(app=app)
    
    async def override_get_db():
        mock_session = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        async def mock_refresh(instance):
            instance.id = uuid.uuid4()
            instance.created_at = datetime.utcnow()
            instance.updated_at = datetime.utcnow()
            
        mock_session.refresh.side_effect = mock_refresh
        yield mock_session
        
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/sessions/", json={"title": "Test QA Session", "user_id": "u-123"})
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test QA Session"
        assert data["user_id"] == "u-123"
        assert "id" in data
        
    app.dependency_overrides.clear()
