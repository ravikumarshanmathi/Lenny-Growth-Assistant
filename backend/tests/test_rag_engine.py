import pytest
from unittest.mock import patch, MagicMock
from app.services.rag_engine import retrieve_grounded_context

@pytest.mark.asyncio
async def test_retrieve_grounded_context():
    """Test vector search queries and context retrieval formatting logic."""
    mock_db = MagicMock()
    
    # Mocking database row results from pgvector
    mock_result = MagicMock()
    mock_row = MagicMock()
    mock_row.episode_title = "Ep 301: Elena Verna"
    mock_row.guest_name = "Elena Verna"
    mock_row.similarity_score = 0.95
    mock_row.chunk_content = "Product-led growth relies on the product being the primary channel."
    mock_row.metadata_json = {"file": "ep301.txt"}
    
    mock_result.fetchall.return_value = [mock_row]
    
    # We must mock awaitable AsyncSession execute
    async def mock_execute(*args, **kwargs):
        return mock_result
        
    mock_db.execute = mock_execute
    
    with patch('app.services.rag_engine.model.encode') as mock_encode:
        # Mock the embedding vector dimension size to 384
        mock_encode.return_value.tolist.return_value = [0.1] * 384
        
        context_str, citations = await retrieve_grounded_context("What is PLG?", mock_db)
        
        # Verify Context String Structure
        assert "Ep 301: Elena Verna" in context_str
        assert "Elena Verna" in context_str
        assert "Product-led growth relies" in context_str
        
        # Verify Citation List Structure
        assert len(citations) == 1
        assert citations[0]["episode_title"] == "Ep 301: Elena Verna"
        assert citations[0]["similarity_score"] == 0.95

@pytest.mark.asyncio
async def test_retrieve_grounded_context_below_threshold():
    """Test that document chunks below the 0.35 similarity threshold return empty context."""
    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_row = MagicMock()
    mock_row.episode_title = "Ep 200: Some Topic"
    mock_row.guest_name = "Guest"
    mock_row.similarity_score = 0.20  # Below 0.35 threshold
    mock_row.chunk_content = "Irrelevant transcript content."
    mock_row.metadata_json = {"file": "ep200.txt"}
    
    mock_result.fetchall.return_value = [mock_row]
    
    async def mock_execute(*args, **kwargs):
        return mock_result
        
    mock_db.execute = mock_execute
    
    context_str, citations = await retrieve_grounded_context("Completely out of scope query", mock_db)
    
    assert context_str == ""
    assert citations == []
