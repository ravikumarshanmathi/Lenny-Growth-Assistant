import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app
from app.db.session import get_db

@pytest.mark.asyncio
async def test_health_check_ok():
    """Verify /health returns 200 OK and diagnostics correctly."""
    
    async def override_get_db():
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        yield mock_session
        
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Patch the specific httpx.AsyncClient class imported in health.py
        with patch('app.api.health.httpx.AsyncClient') as mock_httpx_client_class:
            mock_client_instance = MagicMock()
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_httpx_client_class.return_value.__aenter__.return_value = mock_client_instance
            
            response = await client.get("/health/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["database"] == "connected"
            assert data["ollama"] == "connected"
            assert "api_keys" in data

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_health_check_ollama_down():
    """Verify /health returns degraded status if Ollama is unreachable."""
    async def override_get_db():
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        yield mock_session
        
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch('app.api.health.httpx.AsyncClient') as mock_httpx_client_class:
            mock_client_instance = MagicMock()
            
            mock_client_instance.get = AsyncMock(side_effect=Exception("Connection Refused"))
            mock_httpx_client_class.return_value.__aenter__.return_value = mock_client_instance
            
            response = await client.get("/health/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["ollama"] == "disconnected"

    app.dependency_overrides.clear()
