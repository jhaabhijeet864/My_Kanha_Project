"""
Firebase Authentication Helpers
- Initialize Firebase Admin
- Verify Firebase ID tokens
- Map Firebase users to local users
"""

import os
from pathlib import Path
from typing import Optional, Tuple
import firebase_admin
from firebase_admin import auth as fb_auth
from firebase_admin import credentials

from app.logger import logger
from app.core.auth_service import (
    get_user_by_username,
    update_last_login,
    create_access_token,
)

# Lazy init flag
_initialized = False


def init_firebase_admin() -> None:
    global _initialized
    if _initialized:
        return

    try:
        if not firebase_admin._apps:
            key_path = Path(__file__).parent.parent.parent / "serviceAccountKey.json"
            
            if key_path.exists():
                logger.info(f"Initializing Firebase Admin with service account: {key_path}")
                cred = credentials.Certificate(str(key_path))
                firebase_admin.initialize_app(cred)
            else:
                logger.warning(
                    "serviceAccountKey.json not found. "
                    "Attempting to initialize Firebase Admin with Application Default Credentials. "
                    "This works in Google Cloud environments or if you have run 'gcloud auth application-default login'."
                )
                firebase_admin.initialize_app()
                
        _initialized = True
        logger.info("Firebase Admin initialized successfully.")

    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin: {e}", exc_info=True)
        # It's better to raise the exception to make the configuration error obvious on startup
        raise



def verify_firebase_id_token(id_token: str) -> Optional[dict]:
    """Verify Firebase ID token and return decoded information."""
    try:
        init_firebase_admin()
        decoded = fb_auth.verify_id_token(id_token)
        # decoded includes: uid, email, name, picture, auth_time, iss, aud, etc.
        return decoded
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        return None


def issue_server_jwt_for_user(username: str, email: str) -> Tuple[str, int]:
    """
    Create JWT token for existing user and update last login.
    
    Bug Fix #3: Added null check before accessing user data to prevent crashes.
    Raises ValueError if user not found instead of crashing with NoneType error.
    
    Args:
        username: Username of the user
        email: Email of the user
    
    Returns:
        Tuple of (token, expires_in_hours)
    
    Raises:
        ValueError: If user not found in database
    """
    user = get_user_by_username(username)
    if not user:
        raise ValueError(f"User {username} not found")
    
    token, expires_in = create_access_token(user_id=user["user_id"], username=username, email=email)
    update_last_login(user["user_id"])
    return token, expires_in
