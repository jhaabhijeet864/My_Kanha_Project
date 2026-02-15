"""
Chat Routes
Main endpoint for conversing with Krishna.
Smart routing: skips RAG for casual chat, uses it for spiritual questions.
"""

import json
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from fastapi.responses import StreamingResponse
from typing import Optional, AsyncGenerator
from uuid import uuid4

from app.logger import logger
from app.models.chat_models import ChatRequest, ChatResponse, ConversationHistory, StreamChunk
from app.models.verse_models import VerseSource
from app.rag.retriever import retrieve
from app.rag.formatter import format_system_prompt
from app.llm.inference import generate_response, generate_response_stream
from app.core.safety_rules import check_safety
from app.core.auth_service import verify_token
from app.core.prompt_templates import is_casual_message, needs_spiritual_context
from app.utils.language_detect import detect_language
from app.persistence.conversation_store import (
    load_conversation,
    save_conversation,
    create_conversation,
)

router = APIRouter()


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract user_id from JWT token if provided (optional)."""
    if not authorization:
        return None

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]
    token_data = verify_token(token)
    return token_data.user_id if token_data else None


def _to_verse_source(verse: dict) -> VerseSource:
    """Normalize retrieval dicts into VerseSource model."""
    chapter_raw = verse.get("chapter_number", verse.get("chapter"))
    verse_raw = verse.get("verse_number", verse.get("verse"))

    # Guard against missing/zero values to satisfy validation (>=1)
    if not chapter_raw or not verse_raw:
        raise ValueError("Verse data missing chapter or verse number")

    return VerseSource(
        verse_id=verse.get("verse_id"),
        chapter=int(chapter_raw),
        verse=int(verse_raw),
        chapter_name=verse.get("chapter_name", ""),
        sanskrit=verse.get("sanskrit", ""),
        english=verse.get("english_translation") or verse.get("english", ""),
        hindi=verse.get("hindi_translation") or verse.get("hindi", ""),
        similarity_score=verse.get("similarity_score"),
    )


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, user_id: Optional[str] = Depends(get_optional_user)):
    """
    Main chat endpoint - Converse with Krishna.

    Smart routing:
    - Casual messages (hello, thanks, etc.) -> Quick response, no RAG
    - Spiritual questions -> RAG retrieval + verse context

    Persists conversation to JSON storage and links to authenticated user if provided.
    """
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")

        # Get or create user session
        final_user_id = user_id or request.user_id or str(uuid4())
        session_id = request.session_id

        # Load or create conversation
        if session_id:
            session = load_conversation(final_user_id, session_id)
        else:
            session = create_conversation(final_user_id, request.language or "english")
            session_id = session.session_id

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Detect input language
        detected_language = detect_language(request.message)
        logger.debug(f"Detected language: {detected_language}")

        # Safety check
        safety_result = check_safety(request.message)
        if not safety_result.is_safe:
            logger.warning(f"Safety check failed: {safety_result.reason}")

            # Store the user message and safety redirect
            session.add_message("user", request.message)
            session.add_message("assistant", safety_result.safe_response)
            save_conversation(session)

            return ChatResponse(
                response=safety_result.safe_response,
                sources=[],
                language=detected_language,
                session_id=session_id,
                user_id=final_user_id,
            )

        # SMART ROUTING: Only retrieve verses if it's a spiritual question
        normalized_sources = []

        if needs_spiritual_context(request.message):
            # Spiritual question - retrieve relevant verses from ChromaDB
            retrieved_verses = retrieve(
                query=request.message,
                n_results=request.top_k or 3,  # Reduced from 5 to 3 for focused responses
            )
            logger.debug(f"Spiritual question - retrieved {len(retrieved_verses)} verses")

            for v in retrieved_verses:
                try:
                    normalized_sources.append(_to_verse_source(v))
                except Exception as norm_err:
                    logger.warning(f"Skipping verse with missing identifiers: {norm_err}")
        else:
            # Casual message - skip RAG entirely for faster response
            logger.debug("Casual message detected - skipping verse retrieval")

        # Generate response using LLM (inference.py handles casual vs spiritual)
        response = await generate_response(
            user_message=request.message,
            retrieved_verses=normalized_sources,
            conversation_history=session.get_messages_for_context(),
            response_language=request.language or detected_language,
        )

        # Store messages in session
        sources_for_storage = [s.model_dump() if hasattr(s, 'model_dump') else s.__dict__ for s in normalized_sources] if normalized_sources else []
        session.add_message("user", request.message, sources=sources_for_storage)
        session.add_message("assistant", response.text, sources=sources_for_storage)

        # Save conversation to persistent storage
        save_conversation(session)

        # Convert VerseSource objects to dictionaries for response
        sources_dicts = [s.model_dump() if hasattr(s, 'model_dump') else s for s in response.sources] if response.sources else []

        return ChatResponse(
            response=response.text,
            sources=sources_dicts,  # Will be empty for casual, verses for spiritual
            language=detected_language,
            metadata=response.metadata,
            session_id=session_id,
            user_id=final_user_id,
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")


@router.post("/stream")
async def chat_stream(request: ChatRequest, user_id: Optional[str] = Depends(get_optional_user)):
    """
    Streaming chat endpoint for real-time responses.
    Returns Server-Sent Events (SSE) stream.

    Smart routing: skips RAG for casual messages.
    Optional JWT authentication to link chat history to user.
    """
    try:
        logger.info(f"Received streaming chat request: {request.message[:50]}...")

        # Get or create user session
        final_user_id = user_id or request.user_id or str(uuid4())
        session_id = request.session_id

        # Load or create conversation
        if session_id:
            session = load_conversation(final_user_id, session_id)
        else:
            session = create_conversation(final_user_id, request.language or "english")
            session_id = session.session_id

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Detect input language
        detected_language = detect_language(request.message)

        # Safety check
        safety_result = check_safety(request.message)
        if not safety_result.is_safe:
            logger.warning(f"Safety check failed: {safety_result.reason}")

            async def safety_response():
                chunk = StreamChunk(
                    type="complete",
                    content=safety_result.safe_response,
                    is_complete=True,
                    sources=[],
                )
                yield f"data: {chunk.model_dump_json()}\n\n"

            return StreamingResponse(
                safety_response(),
                media_type="text/event-stream",
            )

        # SMART ROUTING: Only retrieve verses if it's a spiritual question
        normalized_sources = []

        if needs_spiritual_context(request.message):
            retrieved_verses = retrieve(
                query=request.message,
                n_results=request.top_k or 3,  # Reduced from 5 to 3
            )
            logger.debug(f"Streaming spiritual response - retrieved {len(retrieved_verses)} verses")

            for v in retrieved_verses:
                try:
                    normalized_sources.append(_to_verse_source(v))
                except Exception as norm_err:
                    logger.warning(f"Skipping verse with missing identifiers: {norm_err}")
        else:
            logger.debug("Streaming casual response - skipping verse retrieval")

        async def generate_stream() -> AsyncGenerator[str, None]:
            """Generate SSE stream with response chunks."""
            try:
                full_response = ""
                async for chunk_text in generate_response_stream(
                    user_message=request.message,
                    retrieved_verses=normalized_sources,
                    conversation_history=request.conversation_history,
                    response_language=request.language or detected_language,
                ):
                    full_response += chunk_text
                    chunk = StreamChunk(content=chunk_text, is_complete=False)
                    yield f"data: {chunk.model_dump_json()}\n\n"

                # Store messages in session
                sources_for_storage = [s.model_dump() if hasattr(s, 'model_dump') else s.__dict__ for s in normalized_sources] if normalized_sources else []
                session.add_message("user", request.message, sources=sources_for_storage)
                session.add_message("assistant", full_response, sources=sources_for_storage)

                # Save conversation to persistent storage
                save_conversation(session)

                # Send final chunk with sources (empty for casual, verses for spiritual)
                sources_dicts = [s.model_dump() if hasattr(s, 'model_dump') else s for s in normalized_sources] if normalized_sources else []
                final_chunk = StreamChunk(
                    type="complete",
                    content="",
                    is_complete=True,
                    sources=sources_dicts,
                )
                yield f"data: {final_chunk.model_dump_json()}\n\n"

            except Exception as e:
                logger.error(f"Error in stream generation: {e}")
                error_chunk = StreamChunk(
                    content="Hey, I'm having a little trouble right now. Try again?",
                    is_complete=True,
                    sources=[],
                )
                yield f"data: {error_chunk.model_dump_json()}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except Exception as e:
        logger.error(f"Error processing streaming chat request: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")
