"""
ChromaDB Connection Module
Provides access to the ChromaDB vector store.
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.config import settings
from app.rag.retriever import GitaRetriever

logger = logging.getLogger(__name__)

# Paths - now using settings
VECTOR_DB_PATH = Path(settings.CHROMA_PERSIST_DIR)
INIT_FLAG_FILE = VECTOR_DB_PATH / '.initialized'


class ChromaDBConnector:
    """Handles connection to ChromaDB"""
    
    _retriever: Optional[GitaRetriever] = None

    @classmethod
    def get_retriever(cls) -> GitaRetriever:
        """
        Get an initialized retriever instance.
        
        This method is the single point of access to the retriever.
        """
        if cls._retriever is None:
            logger.info("Connecting to ChromaDB and initializing retriever...")
            try:
                cls._retriever = GitaRetriever()
                logger.info("✓ Retriever initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize GitaRetriever: {e}", exc_info=True)
                # Re-raise the exception to prevent the application from starting in a broken state
                raise
        return cls._retriever

    @classmethod
    def check_health(cls) -> dict:
        """Check ChromaDB health status"""
        try:
            retriever = cls.get_retriever()
            return retriever.health_check()
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


def get_collection_stats() -> dict:
    """
    Get statistics about the ChromaDB collection.
    """
    try:
        retriever = ChromaDBConnector.get_retriever()
        health_info = retriever.health_check()
        
        return {
            'status': 'healthy' if health_info.get('status') == 'ok' else 'unhealthy',
            'total_verses_indexed': health_info.get('total_verses_indexed', 0),
            'collections': health_info.get('collections', []),
            'vector_store_location': str(VECTOR_DB_PATH),
            'last_updated': get_last_index_time()
        }
    except Exception as e:
        logger.error(f"Failed to get collection stats: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e)
        }


def get_last_index_time() -> Optional[str]:
    """
    Get timestamp of last successful index operation by checking the .initialized flag.
    
    Returns:
        ISO format timestamp or None if the flag file doesn't exist.
    """
    if INIT_FLAG_FILE.exists():
        try:
            timestamp = INIT_FLAG_FILE.stat().st_mtime
            return datetime.fromtimestamp(timestamp).isoformat()
        except Exception as e:
            logger.error(f"Failed to get index timestamp from flag file: {str(e)}")
            return None
    return None

# The reindex and startup_event functions are removed as the indexing
# is now a separate, manual process. The admin routes that depended
# on reindex will need to be adjusted or removed.