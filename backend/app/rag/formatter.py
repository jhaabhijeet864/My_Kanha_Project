"""
Formatter Module
Formats retrieved verses into structured prompts for LLM processing
"""

import logging
from typing import List, Dict, Any, Optional

from app.models.verse_models import VerseSource

logger = logging.getLogger(__name__)


class FormattedContext:
    """Container for formatted verse context and metadata."""
    def __init__(self, context_text: str, verse_count: int, chapters_referenced: List[int], total_relevance: float = 0.0):
        self.context_text = context_text
        self.verse_count = verse_count
        self.chapters_referenced = chapters_referenced
        self.total_relevance = total_relevance


class VerseFormatter:
    """Format verses for inclusion in system prompts and responses"""
    
    @staticmethod
    def format_for_system_prompt(verses: List[Dict[str, Any]]) -> str:
        """
        Format retrieved verses for inclusion in system prompt
        
        Args:
            verses: List of retrieved verse dictionaries
        
        Returns:
            Formatted string for system prompt
        """
        if not verses:
            return ""
        
        formatted = "## Relevant Bhagavad Gita References:\n\n"
        
        for i, verse in enumerate(verses, 1):
            formatted += f"**Verse {i}: {verse.get('verse_id', 'Unknown')}** (Chapter {verse.get('chapter_number')}, Verse {verse.get('verse_number')})\n"
            formatted += f"*{verse.get('chapter_name', '')}*\n\n"
            
            # Sanskrit text
            if verse.get('sanskrit'):
                formatted += f"**Sanskrit:** {verse['sanskrit']}\n\n"
            
            # English translation
            if verse.get('english_translation'):
                formatted += f"**Translation:** {verse['english_translation']}\n\n"
            
            # Commentary
            if verse.get('commentary'):
                # Truncate long commentary
                commentary = verse['commentary']
                if len(commentary) > 300:
                    commentary = commentary[:300] + "..."
                formatted += f"**Commentary:** {commentary}\n\n"
            
            # Speaker
            if verse.get('speaker'):
                formatted += f"*Spoken by: {verse['speaker']}*\n\n"
            
            formatted += "---\n\n"
        
        return formatted
    
    @staticmethod
    def format_for_chat_response(verses: List[Dict[str, Any]]) -> str:
        """
        Format verses for display in chat response
        
        Args:
            verses: List of retrieved verse dictionaries
        
        Returns:
            Formatted string for chat display
        """
        if not verses:
            return "No relevant verses found."
        
        formatted = "Here are the relevant verses from the Bhagavad Gita:\n\n"
        
        for verse in verses:
            verse_id = verse.get('verse_id', 'Unknown')
            chapter_name = verse.get('chapter_name', '')
            similarity = verse.get('similarity_score', 0)
            
            formatted += f"📖 **{verse_id}** - {chapter_name}"
            if similarity:
                formatted += f" (Relevance: {similarity*100:.0f}%)"
            formatted += "\n"
            
            # English translation
            if verse.get('english_translation'):
                formatted += f"> {verse['english_translation']}\n\n"
            
            formatted += "\n"
        
        return formatted
    
    @staticmethod
    def format_full_verse(verse: Dict[str, Any]) -> str:
        """
        Format a complete verse with all available information
        
        Args:
            verse: Verse dictionary
        
        Returns:
            Fully formatted verse string
        """
        formatted = ""
        
        # Header
        formatted += f"# {verse.get('verse_id', 'Unknown')}\n"
        formatted += f"## {verse.get('chapter_name', '')}\n\n"
        
        # Sanskrit
        if verse.get('sanskrit'):
            formatted += f"### Sanskrit Text\n{verse['sanskrit']}\n\n"
        
        # English Translation
        if verse.get('english_translation'):
            formatted += f"### English Translation\n{verse['english_translation']}\n\n"
        
        # Hindi Translation
        if verse.get('hindi_translation'):
            formatted += f"### Hindi Translation (हिंदी)\n{verse['hindi_translation']}\n\n"
        
        # Commentary
        if verse.get('commentary'):
            formatted += f"### Commentary\n{verse['commentary']}\n\n"
        
        # Speaker
        if verse.get('speaker'):
            formatted += f"### Speaker\n{verse['speaker']}\n\n"
        
        # Similarity score
        if verse.get('similarity_score'):
            formatted += f"### Relevance Score\n{verse['similarity_score']*100:.2f}%\n"
        
        return formatted
    
    @staticmethod
    def format_search_results(verses: List[Dict[str, Any]], query: str) -> str:
        """
        Format search results for display
        
        Args:
            verses: List of retrieved verses
            query: Original search query
        
        Returns:
            Formatted search results
        """
        formatted = f"Search Results for: \"{query}\"\n"
        formatted += f"Found {len(verses)} relevant verse(s)\n\n"
        
        for i, verse in enumerate(verses, 1):
            formatted += f"{i}. **{verse.get('verse_id')}** - {verse.get('chapter_name')}\n"
            
            if verse.get('english_translation'):
                translation = verse['english_translation']
                if len(translation) > 100:
                    translation = translation[:100] + "..."
                formatted += f"   {translation}\n"
            
            if verse.get('similarity_score'):
                formatted += f"   Match: {verse['similarity_score']*100:.0f}%\n"
            
            formatted += "\n"
        
        return formatted
    
    @staticmethod
    def format_chapter_overview(verses: List[Dict[str, Any]], chapter_number: int) -> str:
        """
        Format verses from a chapter as an overview
        
        Args:
            verses: List of verses from a chapter
            chapter_number: Chapter number
        
        Returns:
            Formatted chapter overview
        """
        if not verses:
            return f"Chapter {chapter_number} has no verses."
        
        chapter_name = verses[0].get('chapter_name', 'Unknown')
        formatted = f"# Chapter {chapter_number}: {chapter_name}\n\n"
        formatted += f"**Total Verses:** {len(verses)}\n\n"
        
        formatted += "## Verse List:\n\n"
        
        for verse in verses:
            formatted += f"- **Verse {verse.get('verse_number')}**\n"
            
            if verse.get('english_translation'):
                translation = verse['english_translation']
                if len(translation) > 80:
                    translation = translation[:80] + "..."
                formatted += f"  {translation}\n"
            
            formatted += "\n"
        
        return formatted
    
    @staticmethod
    def create_rag_context(verses: List[Dict[str, Any]], max_tokens: int = 2000) -> str:
        """
        Create RAG context string with token limit awareness
        
        Args:
            verses: Retrieved verses
            max_tokens: Maximum token count (approximate, ~4 chars per token)
        
        Returns:
            RAG context string within token limit
        """
        max_chars = max_tokens * 4
        context = ""
        
        for verse in verses:
            verse_text = f"""
Verse: {verse.get('verse_id')}
Chapter: {verse.get('chapter_name')}
Translation: {verse.get('english_translation')}
Commentary: {verse.get('commentary', '')}
---
"""
            
            if len(context) + len(verse_text) > max_chars:
                context += "\n[Context truncated due to token limit]"
                break
            
            context += verse_text
        
        return context


# Convenience functions
def format_system_prompt(verses: List[Dict[str, Any]]) -> str:
    """Format verses for system prompt"""
    return VerseFormatter.format_for_system_prompt(verses)


def format_chat_response(verses: List[Dict[str, Any]]) -> str:
    """Format verses for chat response"""
    return VerseFormatter.format_for_chat_response(verses)


def format_full_verse(verse: Dict[str, Any]) -> str:
    """Format a complete verse"""
    return VerseFormatter.format_full_verse(verse)


def create_rag_context(verses: List[Dict[str, Any]]) -> str:
    """Create RAG context"""
    return VerseFormatter.create_rag_context(verses)


def format_verse_for_context(
    verse: Any,
    include_sanskrit: bool = True,
    include_transliteration: bool = False,
    include_commentary: bool = True,
    language: str = "english"
) -> str:
    """
    Format a single verse for inclusion in LLM context.
    Safely handles both objects and dictionaries.
    """
    parts = []

    # Helper to get value from either object or dict
    def get_val(obj, attr, default=""):
        if hasattr(obj, attr):
            return getattr(obj, attr)
        if isinstance(obj, dict):
            return obj.get(attr, default)
        return default

    # Header
    chapter = get_val(verse, 'chapter')
    verse_num = get_val(verse, 'verse')
    parts.append(f"**Chapter {chapter}, Verse {verse_num}**")

    # Sanskrit (if requested and available)
    sanskrit = get_val(verse, 'sanskrit')
    if include_sanskrit and sanskrit:
        parts.append(f"Sanskrit: {sanskrit}")

    # Transliteration (if requested and available)
    # Fix Bug 4.2: Support both 'transliteration' and 'transliteration_text'
    transliteration = get_val(verse, 'transliteration') or get_val(verse, 'transliteration_text')
    if include_transliteration and transliteration:
        parts.append(f"Transliteration: {transliteration}")

    # Translation based on language preference
    # Fix Bug 4.3: Case-insensitive language check
    lang_pref = language.lower() if language else "english"
    hindi_val = get_val(verse, 'hindi')
    english_val = get_val(verse, 'english')

    if lang_pref == "hindi" and hindi_val:
        parts.append(f"Translation (Hindi): {hindi_val}")
    elif english_val:
        parts.append(f"Translation: {english_val}")
    elif hindi_val:
        parts.append(f"Translation (Hindi): {hindi_val}")

    # Relevance score (if available)
    score = get_val(verse, 'similarity_score')
    if score:
        try:
            parts.append(f"(Relevance: {float(score):.0%})")
        except (ValueError, TypeError):
            pass

    return "\n".join(parts)


def format_verses_for_prompt(
    verses: List[Any],
    max_verses: int = 5,
    include_sanskrit: bool = True,
    include_transliteration: bool = False,
    language: str = "english"
) -> FormattedContext:
    """
    Format multiple verses into a context block for the LLM prompt.
    Safely handles both VerseSource objects and dictionaries.
    """
    if not verses:
        return FormattedContext(
            context_text="No specific verses found for this query.",
            verse_count=0,
            chapters_referenced=[],
            total_relevance=0.0
        )

    # Helper to get value
    def get_val(obj, attr, default=None):
        if hasattr(obj, attr):
            return getattr(obj, attr)
        if isinstance(obj, dict):
            return obj.get(attr, default)
        return default

    # Limit verses
    verses = verses[:max_verses]

    # Format each verse
    formatted_verses = []
    chapters = set()
    total_relevance = 0.0

    for i, verse in enumerate(verses, 1):
        formatted = format_verse_for_context(
            verse,
            include_sanskrit=include_sanskrit,
            include_transliteration=include_transliteration,
            language=language
        )
        formatted_verses.append(f"[{i}] {formatted}")

        chapter = get_val(verse, 'chapter')
        if chapter:
            chapters.add(chapter)
        
        score = get_val(verse, 'similarity_score')
        if score:
            try:
                total_relevance += float(score)
            except (ValueError, TypeError):
                pass

    # Build context text
    header = f"**Relevant Verses from Bhagavad Gita** ({len(verses)} verses)\n"
    separator = "\n" + "-" * 40 + "\n"
    context_text = header + separator.join(formatted_verses)

    return FormattedContext(
        context_text=context_text,
        verse_count=len(verses),
        chapters_referenced=sorted(list(chapters)),
        total_relevance=total_relevance / len(verses) if verses else 0.0
    )


def format_for_krishna_response(
    query: str,
    verses: List[VerseSource],
    conversation_history: Optional[List[dict]] = None,
    language: str = "english"
) -> str:
    """
    Format the complete context for Krishna's response generation.

    Args:
        query: User's question
        verses: Retrieved relevant verses
        conversation_history: Previous messages (optional)
        language: Preferred response language

    Returns:
        Complete formatted prompt context
    """
    # Format verses
    formatted = format_verses_for_prompt(
        verses,
        max_verses=5,
        include_sanskrit=True,
        language=language
    )

    # Build context sections
    sections = []

    # Verse context
    sections.append("=== RELEVANT GITA WISDOM ===")
    sections.append(formatted.context_text)

    # Conversation history (if any)
    if conversation_history:
        sections.append("\n=== PREVIOUS CONVERSATION ===")
        for msg in conversation_history[-3:]:  # Last 3 messages
            role = "Seeker" if msg.get('role') == 'user' else "Krishna"
            sections.append(f"{role}: {msg.get('content', '')[:200]}")

    # Current query
    sections.append("\n=== SEEKER'S QUESTION ===")
    sections.append(query)

    # Instructions
    sections.append("\n=== RESPONSE INSTRUCTIONS ===")
    if language == "hindi":
        sections.append("- Respond in Hindi (हिंदी में उत्तर दें)")
    else:
        sections.append("- Respond in clear, accessible English")
    sections.append("- Reference the verses above when relevant")
    sections.append("- Provide practical wisdom for the seeker's situation")
    sections.append("- Speak as Krishna with compassion and authority")

    return "\n".join(sections)


def format_verse_citation(verse: VerseSource) -> str:
    """
    Format a verse as a citation reference.

    Args:
        verse: VerseSource object

    Returns:
        Citation string (e.g., "Bhagavad Gita 2:47")
    """
    return f"Bhagavad Gita {verse.chapter}:{verse.verse}"


def format_verse_card(
    verse: VerseSource,
    include_all_languages: bool = False
) -> dict:
    """
    Format a verse as a card/block for display (e.g., in mobile app).

    Args:
        verse: VerseSource object
        include_all_languages: Whether to include all translations

    Returns:
        Dictionary suitable for JSON response
    """
    card = {
        "reference": f"Chapter {verse.chapter}, Verse {verse.verse}",
        "citation": format_verse_citation(verse),
        "sanskrit": verse.sanskrit or None,
        "transliteration": verse.transliteration or None,
        "english": verse.english or None,
    }

    if include_all_languages:
        card["hindi"] = verse.hindi or None

    if verse.similarity_score:
        card["relevance"] = round(verse.similarity_score, 3)

    return card


# ============ Test Utilities ============

def test_retrieval_formatting():
    """
    Test the formatting functions with sample data.
    Run this to verify formatting works correctly.
    """
    # Sample verses
    sample_verses = [
        VerseSource(
            chapter=2,
            verse=47,
            sanskrit="कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
            english="You have the right to work only, but never to its fruits.",
            hindi="कर्म करने में ही तुम्हारा अधिकार है, फल में कभी नहीं।",
            transliteration="karmaṇy evādhikāras te mā phaleṣu kadācana",
            similarity_score=0.92
        ),
        VerseSource(
            chapter=2,
            verse=48,
            sanskrit="योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।",
            english="Perform action, O Arjuna, being steadfast in Yoga, abandoning attachment.",
            hindi="हे धनञ्जय! योग में स्थित होकर कर्म करो।",
            transliteration="yoga-sthaḥ kuru karmāṇi saṅgaṁ tyaktvā dhanañjaya",
            similarity_score=0.85
        ),
    ]

    print("=" * 60)
    print("FORMATTER TEST")
    print("=" * 60)

    # Test single verse formatting
    print("\n--- Single Verse (English) ---")
    print(format_verse_for_context(sample_verses[0], language="english"))

    print("\n--- Single Verse (Hindi) ---")
    print(format_verse_for_context(sample_verses[0], language="hindi"))

    # Test multiple verses
    print("\n--- Multiple Verses Context ---")
    formatted = format_verses_for_prompt(sample_verses)
    print(formatted.context_text)
    print(f"\nVerse Count: {formatted.verse_count}")
    print(f"Chapters: {formatted.chapters_referenced}")
    print(f"Avg Relevance: {formatted.total_relevance:.2%}")

    # Test full Krishna response context
    print("\n--- Full Krishna Response Context ---")
    full_context = format_for_krishna_response(
        query="Why should I work if I might fail?",
        verses=sample_verses,
        language="english"
    )
    print(full_context)

    # Test verse card
    print("\n--- Verse Card (JSON) ---")
    import json
    card = format_verse_card(sample_verses[0], include_all_languages=True)
    print(json.dumps(card, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_retrieval_formatting()
