"""
Retriever Module
Handles semantic search and retrieval of relevant Gita verses from ChromaDB
"""

import logging
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb import PersistentClient
from chromadb.config import Settings

from app.config import settings

logger = logging.getLogger(__name__)

# Paths - now using settings
VECTOR_DB_PATH = Path(settings.CHROMA_PERSIST_DIR)


class GitaRetriever:
    """Retrieve relevant verses from ChromaDB based on semantic similarity"""
    
    def __init__(self):
        """Initialize ChromaDB client with persistent storage"""
        try:
            # Ensure path is absolute if possible
            persist_path = str(VECTOR_DB_PATH.absolute()) if not VECTOR_DB_PATH.is_absolute() else str(VECTOR_DB_PATH)
            
            self.client = PersistentClient(
                path=persist_path,
                settings=Settings(anonymized_telemetry=False),
            )
            self.collection = self.client.get_collection(name="gita_verses")
            logger.info(f"Connected to ChromaDB at {persist_path} with {self.collection.count()} indexed verses")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        distance_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-K most relevant verses for a query
        
        Args:
            query: User query or question
            n_results: Number of top results to return (default: 5)
            distance_threshold: Optional minimum similarity score (0-1)
        
        Returns:
            List of relevant verses with metadata, sorted by relevance
        """
        if not query or not query.strip():
            logger.debug("Empty query received in retriever - returning no results")
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["metadatas", "distances", "documents"],
            )
            
            if not results['ids'] or not results['ids'][0]:
                logger.warning(f"No results found for query: {query}")
                return []
            
            # Format results
            formatted_results = []
            for i, verse_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i] if results.get('distances') else None
                
                # Convert distance to similarity score (0-1, where 1 is most similar)
                similarity = 1 - distance if distance is not None else None
                
                # Skip if below threshold
                if distance_threshold and similarity and similarity < distance_threshold:
                    continue
                
                metadata = results['metadatas'][0][i]
                # Fix Bug 3.3: Robust fallback for chapter/verse numbers
                chapter_val = metadata.get('chapter')
                if chapter_val is None or chapter_val == "":
                    chapter_val = metadata.get('chapter_number', 0)
                
                verse_val = metadata.get('verse')
                if verse_val is None or verse_val == "":
                    verse_val = metadata.get('verse_number', 0)

                verse = {
                    'verse_id': verse_id,
                    'chapter_number': int(chapter_val or 0),
                    'chapter_name': metadata.get('chapter_name_en') or metadata.get('chapter_name_hi', ''),
                    'verse_number': int(verse_val or 0),
                    'sanskrit': metadata.get('sanskrit', ''),
                    'english_translation': metadata.get('english', ''),
                    'hindi_translation': metadata.get('hindi', ''),
                    'commentary': metadata.get('commentary', ''),
                    'speaker': metadata.get('speaker', 'Unknown'),
                    'similarity_score': round(similarity, 4) if similarity else None,
                    'distance': round(distance, 4) if distance else None
                }
                formatted_results.append(verse)
            
            logger.info(f"Retrieved {len(formatted_results)} verses for query: '{query}'")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error retrieving verses: {str(e)}")
            return []
    
    def retrieve_by_chapter(
        self,
        chapter_number: int,
        query: Optional[str] = None,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve verses from a specific chapter, optionally filtered by semantic similarity
        
        Args:
            chapter_number: Chapter number (1-18)
            query: Optional semantic filter query
            n_results: Number of results to return
        
        Returns:
            List of verses from the specified chapter
        """
        try:
            if query:
                # Semantic search within chapter
                all_results = self.retrieve(query, n_results=50)
                chapter_results = [
                    v for v in all_results
                    if v['chapter_number'] == chapter_number
                ][:n_results]
            else:
                # Get all verses from chapter (dummy query)
                all_results = self.collection.get(
                    where={"chapter_number": {"$eq": str(chapter_number)}}
                )
                chapter_results = []
                for i, verse_id in enumerate(all_results['ids']):
                    metadata = all_results['metadatas'][i]
                    verse = {
                        'verse_id': verse_id,
                        'chapter_number': int(metadata.get('chapter_number', 0)),
                        'chapter_name': metadata.get('chapter_name', ''),
                        'verse_number': int(metadata.get('verse_number', 0)),
                        'sanskrit': metadata.get('sanskrit', ''),
                        'english_translation': metadata.get('english_translation', ''),
                        'hindi_translation': metadata.get('hindi_translation', ''),
                        'commentary': metadata.get('commentary', ''),
                        'speaker': metadata.get('speaker', 'Unknown')
                    }
                    chapter_results.append(verse)
            
            logger.info(f"Retrieved {len(chapter_results)} verses from chapter {chapter_number}")
            return chapter_results
        
        except Exception as e:
            logger.error(f"Error retrieving from chapter {chapter_number}: {str(e)}")
            return []
    
    def retrieve_by_speaker(self, speaker: str) -> List[Dict[str, Any]]:
        """
        Retrieve all verses spoken by a specific speaker
        
        Args:
            speaker: Speaker name (e.g., 'Krishna', 'Arjuna')
        
        Returns:
            List of verses by the specified speaker
        """
        try:
            results = self.collection.get(
                where={"speaker": {"$eq": speaker}}
            )
            
            verses = []
            for i, verse_id in enumerate(results['ids']):
                metadata = results['metadatas'][i]
                verse = {
                    'verse_id': verse_id,
                    'chapter_number': int(metadata.get('chapter_number', 0)),
                    'chapter_name': metadata.get('chapter_name', ''),
                    'verse_number': int(metadata.get('verse_number', 0)),
                    'sanskrit': metadata.get('sanskrit', ''),
                    'english_translation': metadata.get('english_translation', ''),
                    'hindi_translation': metadata.get('hindi_translation', ''),
                    'commentary': metadata.get('commentary', ''),
                    'speaker': metadata.get('speaker', 'Unknown')
                }
                verses.append(verse)
            
            logger.info(f"Retrieved {len(verses)} verses by {speaker}")
            return verses
        
        except Exception as e:
            logger.error(f"Error retrieving verses by speaker '{speaker}': {str(e)}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check ChromaDB connection and index health
        
        Returns:
            Dictionary with health status and stats
        """
        try:
            count = self.collection.count()
            return {
                'status': 'healthy',
                'total_verses_indexed': count,
                'vector_db_path': str(VECTOR_DB_PATH),
                'collection_name': 'gita_verses'
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Singleton instance
_retriever = None
_retriever_lock = threading.Lock()
_initialization_error = None


def get_retriever() -> GitaRetriever:
    """
    Get or create the ChromaDB retriever singleton (thread-safe).
    
    Bug Fix #8: Added error tracking to prevent repeated initialization on failure.
    Ensures all threads see the same initialization error instead of retrying infinitely.
    
    Returns:
        GitaRetriever instance
    
    Raises:
        Exception: If ChromaDB initialization failed (cached from first attempt)
    """
    global _retriever, _initialization_error
    if _retriever is None:
        with _retriever_lock:
            # Double-checked locking
            if _retriever is None:
                try:
                    _retriever = GitaRetriever()
                except Exception as e:
                    _initialization_error = e
                    raise
    if _retriever is None and _initialization_error:
        raise _initialization_error
    return _retriever


def retrieve(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """Convenience function for retrieving verses"""
    return get_retriever().retrieve(query, n_results)
