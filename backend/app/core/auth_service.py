"""
Authentication Service
JWT token generation, validation, and user management.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from pathlib import Path

from app.logger import logger
from app.models.user_models import TokenData


# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("CRITICAL: JWT_SECRET_KEY must be set in environment variables for security")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Database path
DB_PATH_ENV = os.getenv("DB_PATH", "./data/users/users.db")
DB_PATH = Path(DB_PATH_ENV)
DB_DIR = DB_PATH.parent
DB_DIR.mkdir(parents=True, exist_ok=True)


def get_db_connection():
    """Get SQLite connection with proper settings for concurrency."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def init_db():
    """Initialize SQLite database for users."""
    try:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT,
                    password_hash TEXT NOT NULL,
                    firebase_uid TEXT UNIQUE,
                    auth_provider TEXT DEFAULT 'local',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)

            # Migrations for new columns
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN firebase_uid TEXT UNIQUE")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'local'")
            except Exception:
                pass
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    language TEXT DEFAULT 'english',
                    sources TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def hash_password(password: str) -> str:
    """Hash password with salt."""
    salt = secrets.token_hex(32)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    try:
        parts = password_hash.split("$")
        if len(parts) != 2:
            logger.error(f"Invalid password hash format - corrupted hash in database")
            raise ValueError("Corrupted password hash in database")
        
        salt, pwd_hash = parts
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return new_hash.hex() == pwd_hash
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_user(username: str, email: str, password: str, full_name: Optional[str] = None) -> dict:
    """Create a new user."""
    try:
        user_id = secrets.token_hex(16)
        password_hash = hash_password(password)
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users (user_id, username, email, full_name, password_hash)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, email, full_name, password_hash))
            
            conn.commit()
            
            logger.info(f"User created: {username}")
            return {
                "user_id": user_id,
                "username": username,
                "email": email,
                "full_name": full_name,
                "created_at": datetime.now()
            }
        finally:
            conn.close()
    except sqlite3.IntegrityError as e:
        logger.error(f"User creation failed: {e}")
        if "username" in str(e):
            raise ValueError("Username already exists")
        elif "email" in str(e):
            raise ValueError("Email already exists")
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise


def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username."""
    try:
        conn = get_db_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, username, email, full_name, password_hash, created_at, last_login
                FROM users
                WHERE (username = ? OR email = ?) AND is_active = 1
            """, (username, username))
            
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email."""
    try:
        conn = get_db_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_id, username, email, full_name, password_hash, firebase_uid, auth_provider, created_at, last_login
                FROM users
                WHERE email = ? AND is_active = 1
                """,
                (email,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error fetching user by email: {e}")
        return None


def get_user_by_firebase_uid(uid: str) -> Optional[dict]:
    """Get user by firebase UID."""
    try:
        conn = get_db_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_id, username, email, full_name, password_hash, firebase_uid, auth_provider, created_at, last_login
                FROM users
                WHERE firebase_uid = ? AND is_active = 1
                """,
                (uid,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error fetching user by firebase uid: {e}")
        return None


def create_or_link_firebase_user(uid: str, email: str, name: Optional[str] = None) -> dict:
    """Create a local user linked to Firebase or return existing."""
    existing = get_user_by_firebase_uid(uid) or get_user_by_email(email)
    if existing:
        # Link UID if missing
        try:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET firebase_uid = ?, auth_provider = 'firebase' WHERE user_id = ?",
                    (uid, existing["user_id"]),
                )
                conn.commit()
            finally:
                conn.close()
        except Exception as e:
            logger.warning(f"Failed to link firebase UID: {e}")
        return existing

    # Create new user with generated username and placeholder password
    try:
        user_id = secrets.token_hex(16)
        username = email.split("@")[0]
        # Generate a random password so column constraint is satisfied
        password_hash = hash_password(secrets.token_hex(16))

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (user_id, username, email, full_name, password_hash, firebase_uid, auth_provider)
                VALUES (?, ?, ?, ?, ?, ?, 'firebase')
                """,
                (user_id, username, email, name, password_hash, uid),
            )
            conn.commit()

            logger.info(f"Firebase user created: {username}")
            return {
                "user_id": user_id,
                "username": username,
                "email": email,
                "full_name": name,
                "firebase_uid": uid,
                "auth_provider": "firebase",
                "created_at": datetime.now(),
            }
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error creating firebase user: {e}")
        raise


def update_last_login(user_id: str) -> None:
    """Update user's last login timestamp."""
    try:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users
                SET last_login = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error updating last login: {e}")


def create_access_token(user_id: str, username: str, email: str) -> tuple[str, int]:
    """Create JWT access token."""
    try:
        expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        
        payload = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "exp": expiration,
            "iat": datetime.utcnow()
        }
        
        token = encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        expires_in = int((expiration - datetime.utcnow()).total_seconds())
        
        return token, expires_in
    except Exception as e:
        logger.error(f"Error creating token: {e}")
        raise


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token."""
    try:
        payload = decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        user_id = payload.get("user_id")
        username = payload.get("username")
        email = payload.get("email")
        
        if not all([user_id, username, email]):
            return None
        
        return TokenData(user_id=user_id, username=username, email=email)
    except ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None
