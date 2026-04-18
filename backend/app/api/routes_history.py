"""
History Routes
Endpoints for managing conversation history and sessions.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Header, Query
from typing import List, Optional
from uuid import uuid4

from app.persistence.conversation_store import (
    ConversationStore,
    load_conversation,
    list_conversations,
    delete_conversation,
    create_conversation,
)
from app.core.auth_service import verify_token
from app.logger import logger

router = APIRouter()


def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Extract and validate JWT token from Authorization header.
    
    Bug Fix #6: Made authorization header Optional with proper null check.
    Returns 401 Unauthorized instead of 422 validation error when header missing.
    
    Args:
        authorization: Authorization header (format: "Bearer <token>")
    
    Returns:
        TokenData with user_id, username, email
    
    Raises:
        HTTPException(401): If header missing, invalid format, or token invalid/expired
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    
    token = parts[1]
    token_data = verify_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


@router.post("/new")
async def create_new_session(
    language: str = Query("english", description="Preferred language"),
    token_data = Depends(get_current_user)
):
    """
    Create a new conversation session for authenticated user.
    
    Returns session ID to use for subsequent messages.
    """
    try:
        session = create_conversation(token_data.user_id, language)
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at,
            "language": session.language,
            "message": "New conversation session created"
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_sessions(token_data = Depends(get_current_user)):
    """
    List all conversation sessions for authenticated user.
    
    Returns a list of sessions with metadata.
    """
    try:
        sessions = list_conversations(token_data.user_id)
        return {
            "user_id": token_data.user_id,
            "total_sessions": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_conversation(
    session_id: str,
    max_messages: Optional[int] = Query(None, ge=1, description="Limit number of messages (must be >= 1)"),
    token_data = Depends(get_current_user)
):
    """
    Get a specific conversation session with all messages.
    
    Bug Fix #11: Added ge=1 validation to prevent negative/zero values.
    Query parameter now rejects invalid values at validation layer.
    
    Args:
        session_id: ID of conversation session to retrieve
        max_messages: Optional limit on number of messages to return (must be >= 1)
        token_data: Authenticated user token data
    
    Returns:
        Session with metadata and messages
    
    Raises:
        HTTPException(404): If session not found
        HTTPException(422): If max_messages validation fails
    """
    try:
        session = load_conversation(token_data.user_id, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = session.messages
        if max_messages:
            messages = messages[-max_messages:]
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at,
            "last_updated": session.last_updated,
            "language": session.language,
            "message_count": len(session.messages),
            "messages": [msg.to_dict() for msg in messages],
            "metadata": session.metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    token_data = Depends(get_current_user)
):
    """
    Delete a conversation session.
    """
    try:
        success = delete_conversation(token_data.user_id, session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "message": "Session deleted successfully",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/stats")
async def get_session_stats(
    session_id: str,
    token_data = Depends(get_current_user)
):
    """
    Get statistics for a conversation session.
    """
    try:
        session = load_conversation(token_data.user_id, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Count user vs assistant messages
        user_messages = sum(1 for msg in session.messages if msg.role == "user")
        assistant_messages = sum(1 for msg in session.messages if msg.role == "assistant")
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at,
            "last_updated": session.last_updated,
            "total_messages": len(session.messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "language": session.language,
            "duration_minutes": compute_session_duration(session),
            "metadata": session.metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/stats")
async def get_user_stats(token_data = Depends(get_current_user)):
    """
    Get overall statistics for authenticated user.
    """
    try:
        stats = ConversationStore.get_user_stats(token_data.user_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/me/cleanup")
async def cleanup_user_sessions(
    max_sessions: int = Query(50, description="Keep only the N most recent sessions"),
    token_data = Depends(get_current_user)
):
    """
    Clean up old sessions, keeping only the N most recent.
    """
    try:
        deleted = ConversationStore.clear_old_sessions(token_data.user_id, max_sessions)
        return {
            "user_id": token_data.user_id,
            "deleted_sessions": deleted,
            "message": f"Cleaned up {deleted} old sessions"
        }
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def compute_session_duration(session) -> float:
    """
    Compute duration of session in minutes.
    
    Bug Fix #7: Replaced bare except with specific exception handling.
    Now logs the actual error for debugging instead of silently returning 0.
    
    Args:
        session: Session object with created_at and last_updated timestamps
    
    Returns:
        Session duration in minutes (rounded to 2 decimals), or 0 if error
    """
    from datetime import datetime
    
    try:
        created = datetime.fromisoformat(session.created_at)
        updated = datetime.fromisoformat(session.last_updated)
        duration = (updated - created).total_seconds() / 60
        return round(duration, 2)
    except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"Error computing session duration: {e}")
        return 0.0
