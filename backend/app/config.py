"""
Application Configuration
Loads settings from environment variables.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
import json
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application
    APP_NAME: str = "Kanha API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Paths
    DATA_PATH: str = "./data/cleaned"
    CHROMA_PERSIST_DIR: str = "./vector_db/chroma"

    # LLM Configuration
    LLM_PROVIDER: str = "groq"  # "groq" for fast cloud API, "ollama" for local
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Groq API Configuration (fast cloud inference)
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"  # Excellent for multilingual spiritual conversations
    
    # Ollama model (used when LLM_PROVIDER is "ollama")
    LLM_MODEL: str = "llama3"
    
    # Temperature: 0.7-0.8 good for creative spiritual responses
    # Lower (0.3-0.5) for more focused, consistent answers
    LLM_TEMPERATURE: float = 0.75
    # Max tokens: 512-768 for concise responses, 1024+ for detailed explanations
    LLM_MAX_TOKENS: int = 768

    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"

    # RAG
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7

    # Security
    API_KEY: str = ""
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "https://my-kanha-apk.web.app",
        "https://my-kanha-apk.firebaseapp.com",
        "https://my-kanha.web.app",
        "https://my-kanha.firebaseapp.com"
    ]
    
    # JWT Authentication
    JWT_SECRET_KEY: str
    JWT_EXPIRATION_HOURS: int = 24

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    # Firebase
    FIREBASE_PROJECT_ID: str = "my-kanha"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string or list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v


# Global settings instance
settings = Settings()
