"""
Inference
Smart context assembly and response generation.
Routes between casual chat and spiritual questions.
"""

from typing import List, Optional, AsyncGenerator
from dataclasses import dataclass, field

from app.logger import logger
from app.llm.local_llm import get_llm_client
from app.core.prompt_templates import (
    KRISHNA_SYSTEM_PROMPT,
    CASUAL_RESPONSE_TEMPLATE,
    SPIRITUAL_RESPONSE_TEMPLATE,
    LANGUAGE_INSTRUCTION,
    is_casual_message,
)
from app.models.verse_models import VerseSource
from app.models.chat_models import ConversationHistory
from app.rag.formatter import format_verses_for_prompt, format_verse_citation


@dataclass
class LLMResponse:
    """Response from LLM inference."""
    text: str
    sources: List[VerseSource] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


async def generate_response(
    user_message: str,
    retrieved_verses: List[VerseSource],
    conversation_history: Optional[List[ConversationHistory]] = None,
    response_language: str = "english",
    max_verses: int = 3,
) -> LLMResponse:
    """
    Generate Krishna's response - smart routing between casual and spiritual.

    For casual messages (greetings, thanks, etc.): Quick, friendly response without verses.
    For spiritual questions: Rich response with verse context woven in naturally.

    Args:
        user_message: The user's question/message
        retrieved_verses: Relevant verses from RAG retrieval (may be empty for casual)
        conversation_history: Previous messages in conversation
        response_language: Desired response language
        max_verses: Max verses to include in context

    Returns:
        LLMResponse with generated text and sources
    """
    # Fix Bug 5.1: Null guard
    if not user_message:
        return LLMResponse(text="My dear seeker, please share your thoughts with me.", sources=[])

    # Build conversation history string
    history = build_history(conversation_history)

    # Check if this is casual chat (no verses needed)
    is_casual = is_casual_message(user_message)

    if is_casual:
        # Casual chat - quick, friendly, no verse dumps
        prompt = CASUAL_RESPONSE_TEMPLATE.format(
            question=user_message,
            history=history if history else "First message - new conversation",
        )
        # Don't include verse sources for casual chat
        sources_to_return = []
        logger.debug(f"Casual message detected, skipping verse context")
    else:
        # Spiritual/deep question - use verse context wisely
        # Fix Bug 5.2: Pass max_verses to build_context
        context = build_context(retrieved_verses, language=response_language, max_verses=max_verses)
        prompt = SPIRITUAL_RESPONSE_TEMPLATE.format(
            context=context,
            question=user_message,
            history=history if history else "First message - new conversation",
        )
        sources_to_return = retrieved_verses
        logger.debug(f"Spiritual question - using {len(retrieved_verses)} verses for context")

    # Add language instruction
    language_instruction = LANGUAGE_INSTRUCTION.get(
        response_language.lower(),
        LANGUAGE_INSTRUCTION["english"]
    )

    system_prompt = f"{KRISHNA_SYSTEM_PROMPT}\n\n{language_instruction}"

    logger.debug(f"Generating response for: {user_message[:50]}...")

    try:
        client = get_llm_client()

        response_text = await client.generate(
            prompt=prompt,
            system=system_prompt,
        )

        # Clean up response
        response_text = clean_response(response_text)

        # Add verse references to metadata only if we used them
        verse_refs = [format_verse_citation(v) for v in sources_to_return[:max_verses]] if sources_to_return else []

        return LLMResponse(
            text=response_text,
            sources=sources_to_return,  # Empty for casual, verses for spiritual
            metadata={
                "model": client.model,
                "message_type": "casual" if is_casual else "spiritual",
                "context_verses": len(sources_to_return),
                "language": response_language,
                "verse_references": verse_refs,
            },
        )

    except Exception as e:
        logger.error(f"Error generating response: {e}")

        # Return a graceful fallback
        return LLMResponse(
            text=(
                "Hey, I'm having a little trouble connecting right now. "
                "Give me a moment and try again? I'm here for you."
            ),
            sources=[],
            metadata={"error": str(e)},
        )


def build_context(verses: List[VerseSource], language: str = "english", max_verses: int = 3) -> str:
    """
    Build concise context string from retrieved verses.
    Designed for natural weaving, not dumping.
    """
    if not verses:
        return "No specific verses retrieved - respond from general Gita wisdom."

    # Use the formatter but limit to top X most relevant
    formatted = format_verses_for_prompt(
        verses[:max_verses],  # Bug 5.2: Respect max_verses parameter
        max_verses=max_verses,
        include_sanskrit=False,  # Skip Sanskrit for cleaner context
        include_transliteration=False,
        language=language
    )

    # Add instruction for natural weaving
    context_instruction = "\n\n[Weave this wisdom naturally into your response. Don't quote blocks.]"

    return formatted.context_text + context_instruction


def build_history(history: Optional[List[ConversationHistory]]) -> str:
    """Build conversation history string - last 5 messages for context."""
    if not history:
        return ""

    history_parts = []

    for msg in history[-5:]:  # Last 5 messages only
        role = "User" if msg.role == "user" else "Krishna"
        # Truncate long messages for context efficiency
        content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
        history_parts.append(f"{role}: {content}")

    return "\n".join(history_parts)


def clean_response(response: str) -> str:
    """Clean up the LLM response."""
    response = response.strip()

    # Remove common artifacts
    prefixes_to_remove = [
        "Response:",
        "Krishna:",
        "As Krishna,",
        "Here is my response:",
        "Kanha:",
        "As Kanha,",
    ]

    for prefix in prefixes_to_remove:
        if response.startswith(prefix):
            response = response[len(prefix):].strip()

    return response


async def generate_response_stream(
    user_message: str,
    retrieved_verses: List[VerseSource],
    conversation_history: Optional[List[ConversationHistory]] = None,
    response_language: str = "english",
    max_verses: int = 3,
) -> AsyncGenerator[str, None]:
    """
    Generate Krishna's response as a stream of text chunks.
    
    Uses same smart routing as non-streaming version.
    Bug Fix #12: Added AsyncGenerator return type annotation for type safety.
    
    Args:
        user_message: The user's question/message
        retrieved_verses: Relevant verses from RAG retrieval
        conversation_history: Previous messages in conversation
        response_language: Desired response language
        max_verses: Max verses to include in context

    Yields:
        Text chunks as they are generated by the LLM
    """
    # Fix Bug 5.1: Null guard
    if not user_message:
        yield "My dear seeker, please share your thoughts with me."
        return

    # Build conversation history string
    history = build_history(conversation_history)

    # Check if this is casual chat
    is_casual = is_casual_message(user_message)

    if is_casual:
        prompt = CASUAL_RESPONSE_TEMPLATE.format(
            question=user_message,
            history=history if history else "First message - new conversation",
        )
        logger.debug("Streaming casual response")
    else:
        # Fix Bug 5.2: Pass max_verses to build_context
        context = build_context(retrieved_verses, language=response_language, max_verses=max_verses)
        prompt = SPIRITUAL_RESPONSE_TEMPLATE.format(
            context=context,
            question=user_message,
            history=history if history else "First message - new conversation",
        )
        logger.debug(f"Streaming spiritual response with {len(retrieved_verses)} verses")

    # Add language instruction
    language_instruction = LANGUAGE_INSTRUCTION.get(
        response_language.lower(),
        LANGUAGE_INSTRUCTION["english"]
    )

    system_prompt = f"{KRISHNA_SYSTEM_PROMPT}\n\n{language_instruction}"

    logger.debug(f"Generating streaming response for: {user_message[:50]}...")

    try:
        client = get_llm_client()

        async for chunk in client.generate_stream(
            prompt=prompt,
            system=system_prompt,
        ):
            yield chunk

    except Exception as e:
        logger.error(f"Error generating streaming response: {e}")
        yield "Hey, I'm having a little trouble right now. Try again in a moment?"


async def generate_verse_explanation(
    verse: VerseSource,
    context_question: Optional[str] = None,
    language: str = "english",
) -> str:
    """
    Generate a detailed explanation of a specific verse.

    Args:
        verse: The verse to explain
        context_question: Optional question to focus the explanation
        language: Response language

    Returns:
        Detailed explanation text
    """
    prompt = f"""My friend wants to understand this verse from the Bhagavad Gita:

Chapter {verse.chapter}, Verse {verse.verse}

Sanskrit: {verse.sanskrit}
Translation: {verse.english or verse.hindi}

{f"They specifically ask: {context_question}" if context_question else ""}

Explain this as their wise friend:
1. What's the core teaching here?
2. How does this apply to modern life?
3. A practical takeaway they can use today

Keep it warm and accessible - no lecturing."""

    language_instruction = LANGUAGE_INSTRUCTION.get(language.lower(), LANGUAGE_INSTRUCTION["english"])
    system_prompt = f"{KRISHNA_SYSTEM_PROMPT}\n\n{language_instruction}"

    try:
        client = get_llm_client()
        response = await client.generate(prompt=prompt, system=system_prompt)
        return clean_response(response)

    except Exception as e:
        logger.error(f"Error generating verse explanation: {e}")
        return "I'm having trouble explaining this right now. Try asking again?"
