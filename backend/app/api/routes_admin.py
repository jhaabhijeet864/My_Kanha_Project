"""
Admin Routes
Administrative endpoints for managing the system.
"""

import time
from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict

from app.config import settings
from app.logger import logger
from app.rag.ingest import reingest_data, get_ingestion_status
from app.rag.embeddings import get_cached_embedding
from app.rag.init_chromadb import get_collection_stats, get_last_index_time

router = APIRouter()

# Performance metrics tracking
class MetricsTracker:
    """Track retrieval and LLM performance metrics."""
    
    def __init__(self):
        self.retrieval_times = []
        self.llm_response_times = []
        self.retrieval_by_query = defaultdict(list)
        self.llm_by_model = defaultdict(list)
        self.error_log = []
        self.request_count = 0
    
    def record_retrieval(self, query: str, duration: float, results_count: int):
        """Record retrieval performance."""
        self.retrieval_times.append(duration)
        self.retrieval_by_query[query].append({
            "duration": duration,
            "results": results_count,
            "timestamp": datetime.now().isoformat()
        })
    
    def record_llm_response(self, model: str, duration: float, tokens: int = 0):
        """Record LLM response performance."""
        self.llm_response_times.append(duration)
        self.llm_by_model[model].append({
            "duration": duration,
            "tokens": tokens,
            "timestamp": datetime.now().isoformat()
        })
    
    def record_error(self, error_type: str, message: str):
        """Record errors."""
        self.error_log.append({
            "type": error_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_stats(self) -> dict:
        """Get aggregated statistics."""
        if not self.retrieval_times:
            avg_retrieval = 0
        else:
            avg_retrieval = sum(self.retrieval_times) / len(self.retrieval_times)
        
        if not self.llm_response_times:
            avg_llm = 0
        else:
            avg_llm = sum(self.llm_response_times) / len(self.llm_response_times)
        
        return {
            "retrieval": {
                "total_queries": len(self.retrieval_times),
                "avg_time": round(avg_retrieval, 3),
                "min_time": round(min(self.retrieval_times), 3) if self.retrieval_times else 0,
                "max_time": round(max(self.retrieval_times), 3) if self.retrieval_times else 0,
            },
            "llm": {
                "total_requests": len(self.llm_response_times),
                "avg_time": round(avg_llm, 3),
                "min_time": round(min(self.llm_response_times), 3) if self.llm_response_times else 0,
                "max_time": round(max(self.llm_response_times), 3) if self.llm_response_times else 0,
            },
            "errors": {
                "total": len(self.error_log),
                "recent": self.error_log[-10:],
            }
        }

# Global metrics instance
metrics_tracker = MetricsTracker()


def require_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Verify admin API key - enforce authentication for all admin endpoints.
    
    Never allows unauthenticated access to admin endpoints, even in DEBUG mode.
    """
    if not settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Admin endpoints require API key configuration"
        )
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# Keep old name for backward compatibility
verify_admin_key = require_api_key


@router.post("/reindex")
async def trigger_reindex(
    allow_reset: bool = True,
    x_api_key: Optional[str] = Header(None)
):
    """
    Trigger re-indexing of the Gita data into ChromaDB.
    
    NOTE: Reindexing is now a manual process. Use the data pipeline scripts instead.

    Args:
        allow_reset: If True (default), clear existing collection before indexing

    Requires admin API key (X-API-Key header).
    """
    require_api_key(x_api_key)

    # Reindexing has been moved to a manual process
    raise HTTPException(
        status_code=501,
        detail="Reindexing is now a manual process. Please run the data pipeline scripts directly."
    )


@router.get("/status")
async def get_status(x_api_key: Optional[str] = Header(None)):
    """
    Get current system status including ingestion status.
    """
    require_api_key(x_api_key)

    status = await get_ingestion_status()

    return {
        "system": {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG,
            "llm_model": settings.LLM_MODEL,
            "embedding_model": settings.EMBEDDING_MODEL,
        },
        "ingestion": status,
    }


@router.get("/stats")
async def get_stats(x_api_key: Optional[str] = Header(None)):
    """
    Get ChromaDB collection statistics.

    Returns:
        - status: healthy/unhealthy
        - total_verses_indexed: Number of verses in the collection
        - vector_db_path: Path to ChromaDB persistence directory
        - collection_name: Name of the ChromaDB collection
        - last_index_time: Timestamp of last successful indexing
        - embedding_model: Model used for embeddings
        - ollama_model: LLM model configured
    """
    require_api_key(x_api_key)

    logger.info("Admin requested collection stats")

    stats = get_collection_stats()

    return {
        "status": stats["status"],
        "total_verses_indexed": stats["total_verses_indexed"],
        "vector_db_path": stats["vector_db_path"],
        "collection_name": stats["collection_name"],
        "last_index_time": stats["last_index_time"],
        "embedding_model": stats["embedding_model"],
        "ollama_model": stats["ollama_model"],
        "error": stats.get("error"),
    }


@router.get("/llm-status")
async def get_llm_status(x_api_key: Optional[str] = Header(None)):
    """
    Check Ollama LLM availability and latency.

    Returns:
        - reachable: Whether Ollama server is reachable
        - model: Configured LLM model name
        - ollama_url: Ollama base URL
        - latency_ms: Response latency in milliseconds (if reachable)
        - available_models: List of models available in Ollama (if reachable)
    """
    require_api_key(x_api_key)

    logger.info("Admin requested LLM status")

    import httpx

    result = {
        "reachable": False,
        "model": settings.LLM_MODEL,
        "ollama_url": settings.OLLAMA_BASE_URL,
        "latency_ms": None,
        "available_models": [],
        "error": None,
    }

    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")

        latency = (time.time() - start_time) * 1000  # Convert to ms

        if response.status_code == 200:
            result["reachable"] = True
            result["latency_ms"] = round(latency, 2)

            data = response.json()
            result["available_models"] = [
                model["name"] for model in data.get("models", [])
            ]

            # Check if configured model is available
            model_available = any(
                settings.LLM_MODEL in m for m in result["available_models"]
            )
            if not model_available and result["available_models"]:
                result["warning"] = (
                    f"Configured model '{settings.LLM_MODEL}' not found. "
                    f"Available: {result['available_models']}"
                )
        else:
            result["error"] = f"Ollama returned status {response.status_code}"

    except httpx.TimeoutException:
        result["error"] = "Connection to Ollama timed out"
    except httpx.ConnectError:
        result["error"] = f"Cannot connect to Ollama at {settings.OLLAMA_BASE_URL}"
    except Exception as e:
        result["error"] = str(e)

    return result


@router.post("/clear-cache")
async def clear_cache(x_api_key: Optional[str] = Header(None)):
    """
    Clear any cached data including embedding caches.
    """
    require_api_key(x_api_key)

    logger.info("Admin triggered cache clear")

    caches_cleared = []

    try:
        # Clear embedding cache
        cache_info_before = get_cached_embedding.cache_info()
        get_cached_embedding.cache_clear()
        cache_info_after = get_cached_embedding.cache_info()
        caches_cleared.append({
            "cache": "embedding_cache",
            "entries_cleared": cache_info_before.currsize,
        })
        logger.info(f"Cleared embedding cache: {cache_info_before.currsize} entries")

    except Exception as e:
        logger.error(f"Error clearing embedding cache: {e}")
        caches_cleared.append({
            "cache": "embedding_cache",
            "error": str(e),
        })

    return {
        "status": "success",
        "message": "Cache cleared",
        "details": caches_cleared,
    }

@router.get("/stats/retrieval")
async def get_retrieval_stats(x_api_key: Optional[str] = Header(None)):
    """
    Get retrieval performance statistics.
    Shows metrics on vector database queries and retrieval times.
    """
    require_api_key(x_api_key)

    logger.info("Admin requested retrieval stats")
    
    stats = metrics_tracker.get_stats()
    
    return {
        "status": "success",
        "retrieval_stats": stats["retrieval"],
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/stats/llm")
async def get_llm_stats(x_api_key: Optional[str] = Header(None)):
    """
    Get LLM performance statistics.
    Shows metrics on response generation times and model performance.
    """
    require_api_key(x_api_key)

    logger.info("Admin requested LLM stats")
    
    stats = metrics_tracker.get_stats()
    
    return {
        "status": "success",
        "llm_stats": stats["llm"],
        "model": settings.LLM_MODEL,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/stats/combined")
async def get_combined_stats(x_api_key: Optional[str] = Header(None)):
    """
    Get comprehensive performance statistics for both retrieval and LLM.
    """
    require_api_key(x_api_key)

    logger.info("Admin requested combined stats")
    
    stats = metrics_tracker.get_stats()
    
    return {
        "status": "success",
        "stats": stats,
        "models": {
            "llm": settings.LLM_MODEL,
            "embedding": settings.EMBEDDING_MODEL,
        },
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/stats/reset")
async def reset_stats(x_api_key: Optional[str] = Header(None)):
    """
    Reset all performance statistics.
    """
    require_api_key(x_api_key)

    logger.warning("Admin triggered stats reset")
    
    metrics_tracker.retrieval_times.clear()
    metrics_tracker.llm_response_times.clear()
    metrics_tracker.retrieval_by_query.clear()
    metrics_tracker.llm_by_model.clear()
    metrics_tracker.error_log.clear()
    
    return {
        "status": "success",
        "message": "Statistics reset successfully",
    }


@router.get("/health/detailed")
async def get_detailed_health(x_api_key: Optional[str] = Header(None)):
    """
    Get detailed health check including performance metrics and system info.
    """
    require_api_key(x_api_key)

    stats = metrics_tracker.get_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG,
        },
        "models": {
            "llm": settings.LLM_MODEL,
            "embedding": settings.EMBEDDING_MODEL,
        },
        "performance": stats,
    }