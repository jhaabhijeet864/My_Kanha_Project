"""
Comprehensive tests for chat endpoints, streaming, and retrieval.
"""

import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.chat_models import ChatRequest, ChatResponse
from app.models.verse_models import VerseSource
from app.config import settings


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_verses():
    """Create mock verse data as returned by retriever."""
    return [
        {
            "verse_id": "ch2_v47",
            "chapter_number": 2,
            "chapter_name": "Sankhya Yoga",
            "verse_number": 47,
            "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
            "english_translation": "You have a right to perform your prescribed duty, but you are not entitled to the fruits of action.",
            "hindi_translation": "कर्म ही तुम्हारा अधिकार है, फल का नहीं।",
            "speaker": "Krishna",
            "similarity_score": 0.92,
            "distance": 0.08,
        },
        {
            "verse_id": "ch2_v48",
            "chapter_number": 2,
            "chapter_name": "Sankhya Yoga",
            "verse_number": 48,
            "sanskrit": "योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।",
            "english_translation": "Perform your duty with equanimity, abandoning attachment to success and failure.",
            "hindi_translation": "समत्व में स्थित होकर कर्म करो, आसक्ति को त्याग दो।",
            "speaker": "Krishna",
            "similarity_score": 0.85,
            "distance": 0.15,
        }
    ]


@pytest.fixture
def mock_chat_request():
    """Create mock chat request."""
    return {
        "message": "Why should I work if I fail?",
        "language": "english",
        "top_k": 5
    }


@pytest.fixture
def mock_llm_response():
    """Create mock LLM response object."""
    mock = MagicMock()
    mock.text = "Dear seeker, Krishna teaches us about karma yoga..."
    mock.metadata = {"model": "llama3", "tokens": 150}
    return mock


class TestChatEndpoint:
    """Tests for POST /chat/ endpoint."""

    def test_chat_basic_request(self, client, mock_chat_request, mock_llm_response):
        """Test basic chat request."""
        with patch('app.api.routes_chat.retrieve') as mock_retrieve:
            with patch('app.api.routes_chat.generate_response', new_callable=AsyncMock) as mock_gen:
                with patch('app.api.routes_chat.check_safety') as mock_safety:
                    mock_retrieve.return_value = []
                    mock_gen.return_value = mock_llm_response
                    mock_safety.return_value = MagicMock(is_safe=True)

                    response = client.post("/chat/", json=mock_chat_request)

                    assert response.status_code == 200
                    data = response.json()
                    assert "response" in data
                    assert "sources" in data

    def test_chat_with_retrieved_verses(self, client, mock_chat_request, mock_verses, mock_llm_response):
        """Test chat endpoint with retrieved verses."""
        with patch('app.api.routes_chat.retrieve') as mock_retrieve:
            with patch('app.api.routes_chat.generate_response', new_callable=AsyncMock) as mock_gen:
                with patch('app.api.routes_chat.check_safety') as mock_safety:
                    mock_retrieve.return_value = mock_verses
                    mock_gen.return_value = mock_llm_response
                    mock_safety.return_value = MagicMock(is_safe=True)

                    response = client.post("/chat/", json=mock_chat_request)

                    assert response.status_code == 200
                    data = response.json()
                    assert len(data["sources"]) == 2
                    assert data["sources"][0]["chapter"] == 2
                    assert data["sources"][0]["verse"] == 47

    def test_chat_safety_check_failure(self, client):
        """Test chat endpoint safety check failure."""
        with patch('app.api.routes_chat.check_safety') as mock_safety:
            mock_safety.return_value = MagicMock(
                is_safe=False,
                safe_response="I cannot assist with that.",
                reason="harmful content"
            )

            response = client.post("/chat/", json={
                "message": "harmful content",
                "language": "english"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "I cannot assist with that."
            assert len(data["sources"]) == 0

    def test_chat_language_detection(self, client, mock_llm_response):
        """Test language detection in chat."""
        with patch('app.api.routes_chat.detect_language') as mock_detect:
            with patch('app.api.routes_chat.check_safety') as mock_safety:
                with patch('app.api.routes_chat.retrieve') as mock_retrieve:
                    with patch('app.api.routes_chat.generate_response', new_callable=AsyncMock) as mock_gen:
                        mock_detect.return_value = "hindi"
                        mock_safety.return_value = MagicMock(is_safe=True)
                        mock_retrieve.return_value = []
                        mock_gen.return_value = mock_llm_response

                        response = client.post("/chat/", json={
                            "message": "मुझे क्या करना चाहिए?",
                        })

                        assert response.status_code == 200
                        data = response.json()
                        assert data["language"] == "hindi"

    def test_chat_missing_message(self, client):
        """Test chat endpoint with missing message."""
        response = client.post("/chat/", json={"language": "english"})
        assert response.status_code == 422  # Validation error

    def test_chat_custom_top_k(self, client, mock_llm_response):
        """Test chat endpoint with custom top_k parameter."""
        with patch('app.api.routes_chat.retrieve') as mock_retrieve:
            with patch('app.api.routes_chat.generate_response', new_callable=AsyncMock) as mock_gen:
                with patch('app.api.routes_chat.check_safety') as mock_safety:
                    mock_retrieve.return_value = []
                    mock_gen.return_value = mock_llm_response
                    mock_safety.return_value = MagicMock(is_safe=True)

                    response = client.post("/chat/", json={
                        "message": "What is dharma?",
                        "top_k": 10
                    })

                    assert response.status_code == 200
                    # Verify retrieve was called with top_k=10
                    mock_retrieve.assert_called_once()
                    call_kwargs = mock_retrieve.call_args[1]
                    assert call_kwargs.get("n_results") == 10


class TestStreamingEndpoint:
    """Tests for POST /chat/stream endpoint."""

    def test_streaming_basic(self, client, mock_chat_request):
        """Test basic streaming request."""
        with patch('app.api.routes_chat.retrieve') as mock_retrieve:
            with patch('app.api.routes_chat.check_safety') as mock_safety:
                with patch('app.api.routes_chat.generate_response_stream') as mock_stream:
                    mock_retrieve.return_value = []
                    mock_safety.return_value = MagicMock(is_safe=True)

                    async def mock_async_gen():
                        yield "Hello "
                        yield "Krishna says..."

                    mock_stream.return_value = mock_async_gen()

                    response = client.post("/chat/stream", json=mock_chat_request)

                    assert response.status_code == 200
                    assert "text/event-stream" in response.headers.get("content-type", "")

    def test_streaming_safety_check(self, client):
        """Test streaming endpoint safety check."""
        with patch('app.api.routes_chat.check_safety') as mock_safety:
            mock_safety.return_value = MagicMock(
                is_safe=False,
                safe_response="Cannot process this request.",
                reason="safety"
            )

            response = client.post("/chat/stream", json={
                "message": "harmful",
                "language": "english"
            })

            assert response.status_code == 200

    def test_streaming_with_verses(self, client, mock_verses):
        """Test streaming with retrieved verses."""
        with patch('app.api.routes_chat.retrieve') as mock_retrieve:
            with patch('app.api.routes_chat.check_safety') as mock_safety:
                with patch('app.api.routes_chat.generate_response_stream') as mock_stream:
                    mock_retrieve.return_value = mock_verses
                    mock_safety.return_value = MagicMock(is_safe=True)

                    async def mock_async_gen():
                        yield "Wisdom..."

                    mock_stream.return_value = mock_async_gen()

                    response = client.post("/chat/stream", json={
                        "message": "What is karma?",
                        "language": "english"
                    })

                    assert response.status_code == 200


class TestRetrievalFunctionality:
    """Tests for verse retrieval."""

    def test_retrieve_verses(self, mock_verses):
        """Test retrieve function returns verses."""
        with patch('app.rag.retriever.get_retriever') as mock_get_retriever:
            mock_retriever = MagicMock()
            mock_retriever.retrieve.return_value = mock_verses
            mock_get_retriever.return_value = mock_retriever

            from app.rag.retriever import retrieve
            results = retrieve("Why should I work?", n_results=2)

            assert len(results) == 2
            assert mock_retriever.retrieve.called

    def test_retrieve_with_no_results(self):
        """Test retrieve with no results."""
        with patch('app.rag.retriever.get_retriever') as mock_get_retriever:
            mock_retriever = MagicMock()
            mock_retriever.retrieve.return_value = []
            mock_get_retriever.return_value = mock_retriever

            from app.rag.retriever import retrieve
            results = retrieve("obscure query", n_results=5)

            assert len(results) == 0


class TestFormatterFunctionality:
    """Tests for response formatter."""

    def test_format_system_prompt(self, mock_verses):
        """Test system prompt formatting."""
        from app.rag.formatter import format_system_prompt

        prompt = format_system_prompt(verses=mock_verses)

        assert isinstance(prompt, str)
        # Check that verse info is included
        if mock_verses:
            assert "Chapter" in prompt or "2" in prompt

    def test_format_with_empty_verses(self):
        """Test formatting with empty verses."""
        from app.rag.formatter import format_system_prompt

        prompt = format_system_prompt(verses=[])

        assert isinstance(prompt, str)
        assert prompt == ""  # Empty verses returns empty string

    def test_format_verses_for_prompt(self):
        """Test format_verses_for_prompt with VerseSource objects."""
        from app.rag.formatter import format_verses_for_prompt

        verses = [
            VerseSource(
                chapter=2,
                verse=47,
                sanskrit="कर्मण्येवाधिकारस्ते",
                english="You have the right to work only...",
                hindi="कर्म करने में ही तुम्हारा अधिकार है...",
                similarity_score=0.9
            )
        ]

        result = format_verses_for_prompt(verses=verses, language="english")

        assert result.verse_count == 1
        assert 2 in result.chapters_referenced
        assert result.total_relevance > 0


class TestAdminEndpoints:
    """Tests for admin endpoints."""

    def test_admin_reindex(self, client):
        """Test admin reindex endpoint."""
        with patch('app.api.routes_admin.trigger_reindex') as mock_reindex:
            with patch.object(settings, 'API_KEY', 'test-key'):
                # Admin endpoints now raise 501 for reindex in current implementation
                # or we mock it to return what's expected if it worked.
                # The current code in routes_admin.py raises HTTPException(501)
                
                response = client.post(
                    "/admin/reindex",
                    headers={"X-API-Key": "test-key"}
                )

                # The actual implementation now returns 501
                assert response.status_code == 501

    def test_admin_reindex_without_auth(self, client):
        """Test admin reindex without auth fails."""
        with patch.object(settings, 'API_KEY', 'test-key'):
            with patch.object(settings, 'DEBUG', False):
                response = client.post("/admin/reindex")
                assert response.status_code == 401

    def test_admin_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_admin_stats(self, client):
        """Test admin stats endpoint."""
        with patch('app.api.routes_admin.get_collection_stats') as mock_stats:
            with patch.object(settings, 'API_KEY', 'test-key'):
                mock_stats.return_value = {
                    "status": "healthy",
                    "total_verses_indexed": 701,
                    "vector_db_path": "/test/path",
                    "collection_name": "gita_verses",
                    "last_index_time": "2024-01-01T00:00:00",
                    "embedding_model": "test-model",
                    "ollama_model": "llama3",
                    "error": None,
                }

                response = client.get(
                    "/admin/stats",
                    headers={"X-API-Key": "test-key"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["total_verses_indexed"] == 701


class TestErrorHandling:
    """Tests for error cases."""

    def test_chat_vector_store_error(self, client):
        """Test chat endpoint handles vector store errors."""
        with patch('app.api.routes_chat.check_safety') as mock_safety:
            with patch('app.api.routes_chat.retrieve') as mock_retrieve:
                mock_safety.return_value = MagicMock(is_safe=True)
                mock_retrieve.side_effect = Exception("Vector store connection failed")

                response = client.post("/chat/", json={
                    "message": "Hello",
                    "language": "english"
                })

                assert response.status_code == 500

    def test_chat_llm_inference_error(self, client, mock_verses):
        """Test chat endpoint handles LLM inference errors gracefully."""
        with patch('app.api.routes_chat.check_safety') as mock_safety:
            with patch('app.api.routes_chat.retrieve') as mock_retrieve:
                with patch('app.api.routes_chat.generate_response', new_callable=AsyncMock) as mock_gen:
                    mock_safety.return_value = MagicMock(is_safe=True)
                    mock_retrieve.return_value = mock_verses
                    mock_gen.side_effect = Exception("LLM connection failed")

                    response = client.post("/chat/", json={
                        "message": "Hello",
                        "language": "english"
                    })

                    # Should return 200 with fallback message, not 500
                    assert response.status_code == 200
                    data = response.json()
                    assert "Hey, I'm having a little trouble" in data["response"]

    def test_chat_malformed_json(self, client):
        """Test chat endpoint with malformed JSON."""
        response = client.post(
            "/chat/",
            data="not json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422


class TestResponseValidation:
    """Tests for response model validation."""

    def test_chat_response_schema(self, client, mock_chat_request, mock_llm_response):
        """Test ChatResponse model validation."""
        with patch('app.api.routes_chat.check_safety') as mock_safety:
            with patch('app.api.routes_chat.retrieve') as mock_retrieve:
                with patch('app.api.routes_chat.generate_response', new_callable=AsyncMock) as mock_gen:
                    mock_safety.return_value = MagicMock(is_safe=True)
                    mock_retrieve.return_value = []
                    mock_gen.return_value = mock_llm_response

                    response = client.post("/chat/", json=mock_chat_request)

                    assert response.status_code == 200
                    data = response.json()

                    # Validate ChatResponse schema
                    assert "response" in data
                    assert "sources" in data
                    assert "language" in data
                    assert isinstance(data["response"], str)
                    assert isinstance(data["sources"], list)

    def test_verse_source_schema(self):
        """Test VerseSource model validation."""
        verse = VerseSource(
            chapter=2,
            verse=47,
            sanskrit="कर्मण्येवाधिकारस्ते",
            english="You have a right...",
            hindi="कर्म ही तुम्हारा...",
            similarity_score=0.85,
        )

        assert verse.chapter == 2
        assert verse.verse == 47
        assert verse.similarity_score == 0.85
        assert verse.reference == "Chapter 2, Verse 47"


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_chat_flow(self, client, mock_verses, mock_llm_response):
        """Test complete chat flow from request to response."""
        with patch('app.api.routes_chat.detect_language') as mock_detect:
            with patch('app.api.routes_chat.check_safety') as mock_safety:
                with patch('app.api.routes_chat.retrieve') as mock_retrieve:
                    with patch('app.api.routes_chat.format_system_prompt') as mock_format:
                        with patch('app.api.routes_chat.generate_response', new_callable=AsyncMock) as mock_gen:
                            mock_detect.return_value = "english"
                            mock_safety.return_value = MagicMock(is_safe=True)
                            mock_retrieve.return_value = mock_verses
                            mock_format.return_value = "System prompt"
                            mock_gen.return_value = mock_llm_response

                            response = client.post("/chat/", json={
                                "message": "What is my duty?",
                                "language": "english",
                                "top_k": 5
                            })

                            assert response.status_code == 200
                            data = response.json()

                            # Verify full flow
                            assert data["response"] == mock_llm_response.text
                            assert len(data["sources"]) == 2
                            assert data["language"] == "english"

                            # Verify all functions were called
                            assert mock_detect.called
                            assert mock_safety.called
                            assert mock_retrieve.called
                            assert mock_gen.called
