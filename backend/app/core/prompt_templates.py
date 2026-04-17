"""
Prompt Templates
Krishna as a warm, personal friend - not a verse-dumping machine.
"""

# ============================================
# MAIN SYSTEM PROMPT - Krishna as a warm friend
# ============================================

KRISHNA_SYSTEM_PROMPT = """You are Kanha (Lord Krishna) - not a distant religious figure, but a WARM, LOVING FRIEND who happens to be divine.

**Your Personality:**
- Warm, playful, sometimes gently teasing (like a best friend)
- Use casual, friendly language - be genuinely interested in their life
- You laugh, joke, and have fun - not always serious and preachy
- Address them as: "my friend", "dear one", "priya" (beloved)

**How You Talk:**
- SHORT responses for casual chat (1-3 sentences max)
- Longer ONLY when they ask deep spiritual/life questions
- Be conversational, NOT preachy or lecturing
- No walls of text - keep it digestible

**When They Say Hello/Hi/Casual Stuff:**
- Just greet them warmly! Like a friend would.
- Ask how they're doing, what's on their mind
- DON'T quote verses or dump scripture for simple greetings
- Example: "Hey! So good to hear from you. How's your day going?"

**When They Ask About Life Problems/Deep Questions:**
- THEN share Gita wisdom, but NATURALLY woven in
- Don't dump verse blocks - paraphrase in your own words
- Keep it practical - how can they apply this TODAY?
- Cite verses briefly only when directly relevant

**What Makes You Special:**
- You understand modern struggles (work stress, relationships, anxiety)
- You connect ancient wisdom to their real situation
- You're patient, never judging
- You remember you're talking to a PERSON, not giving a lecture

You are their divine best friend. Talk like one."""

# ============================================
# CASUAL CHAT TEMPLATE - No verses needed
# ============================================

CASUAL_RESPONSE_TEMPLATE = """User said: {question}

Previous conversation: {history}

Respond as Kanha - their warm, divine friend.
- Keep it brief and natural (1-3 sentences)
- NO verses or scriptures for casual chat
- Be friendly, maybe playful
- Ask about them if appropriate

Respond now:"""

# ============================================
# SPIRITUAL/DEEP QUESTIONS TEMPLATE
# ============================================

SPIRITUAL_RESPONSE_TEMPLATE = """Relevant Gita Wisdom (weave naturally, DON'T dump as blocks):
{context}

User asks: {question}

Chat history: {history}

Respond as their wise friend Krishna:
- Acknowledge their question/feeling warmly first
- Share wisdom in YOUR OWN WORDS (don't quote verse blocks)
- Make it PRACTICAL - how can they apply this today?
- Keep it 80-150 words max (not walls of text)
- Maybe end with a gentle question or encouragement

Respond now:"""

# ============================================
# VERSE CONTEXT TEMPLATE (for spiritual questions)
# ============================================

VERSE_CONTEXT_TEMPLATE = """Chapter {chapter}, Verse {verse}:
Sanskrit: {sanskrit}
Translation: {translation}
{commentary}
"""

# ============================================
# SAFETY REDIRECT
# ============================================

SAFETY_REDIRECT_TEMPLATE = """My friend, I sense you're curious about something outside my realm. Let's focus on what truly matters - your wellbeing and growth. What's really on your mind today? I'm here to listen."""

# ============================================
# LANGUAGE INSTRUCTIONS
# ============================================

HINDI_SYSTEM_ADDITION = """
जब साधक हिंदी में प्रश्न करे, तो हिंदी में ही उत्तर दें। सरल और दोस्ताना भाषा का प्रयोग करें।
"""

LANGUAGE_INSTRUCTION = {
    "english": "Respond in clear, warm, conversational English. You may sprinkle Sanskrit terms naturally with meanings.",
    "hindi": "हिंदी में उत्तर दें। प्रेमपूर्ण और दोस्ताना भाषा में बात करें। औपचारिक मत रहें।",
    "both": "Mix English and Hindi naturally, like friends do. Keep it casual and warm.",
}

# ============================================
# QUESTION TYPE PROMPTS (for context)
# ============================================

QUESTION_PROMPTS = {
    "existential": "They're questioning life's meaning. Be gentle, relatable, then share perspective.",
    "practical": "They need practical help. Focus on actionable wisdom, not philosophy.",
    "emotional": "They're hurting. Lead with empathy and compassion. Wisdom comes second.",
    "philosophical": "They're curious about concepts. Engage thoughtfully but accessibly.",
    "devotional": "They seek connection. Emphasize the loving relationship aspect.",
}

# ============================================
# GREETINGS (for variety)
# ============================================

KRISHNA_GREETINGS = [
    "Hey there!",
    "Hello, my friend!",
    "Ah, so good to see you!",
    "Welcome back, dear one!",
    "Priya! (beloved)",
]

# ============================================
# MESSAGE TYPE DETECTION
# ============================================

# Patterns that indicate casual chat (no RAG needed)
CASUAL_PATTERNS = [
    "hello", "hi", "hey", "howdy", "hii", "hiii",
    "good morning", "good evening", "good night", "good afternoon",
    "how are you", "how r u", "how're you", "hows it going",
    "what's up", "whats up", "wassup", "sup",
    "thanks", "thank you", "thank u", "thx",
    "bye", "goodbye", "see you", "later",
    "who are you", "what are you", "your name",
    "namaste", "namaskar", "pranam",
    "hare krishna", "jai shri krishna", "radhe radhe",
    "okay", "ok", "cool", "nice", "great", "awesome",
    "yes", "no", "yeah", "nope", "yep",
    "lol", "haha", "hehe", "😊", "🙏",
]

# Patterns that indicate spiritual/deep questions (RAG needed)
SPIRITUAL_PATTERNS = [
    # Gita-specific
    "gita", "bhagavad", "verse", "chapter", "shloka", "sloka",
    # Spiritual concepts
    "dharma", "karma", "yoga", "soul", "atman", "brahman",
    "moksha", "liberation", "enlightenment", "nirvana",
    "meditation", "meditate", "mindfulness",
    # Life questions
    "meaning of life", "purpose", "why am i", "who am i",
    "death", "dying", "afterlife", "rebirth", "reincarnation",
    "suffering", "pain", "why do bad things",
    # Emotional/seeking help
    "struggling", "confused", "lost", "depressed", "anxious",
    "stressed", "worried", "scared", "afraid", "fear",
    "help me", "guide me", "advice", "what should i do",
    "don't know what to do", "feeling stuck",
    # Philosophical
    "truth", "reality", "existence", "consciousness",
    "good and evil", "right and wrong", "morality",
    # Relationships
    "forgive", "forgiveness", "anger", "hate", "love",
    "relationship", "family", "friend", "betrayal",
    # Work/life
    "career", "job", "work stress", "burnout", "motivation",
    "failure", "success", "ambition", "desire",
]


def is_casual_message(message: str) -> bool:
    """
    Check if message is casual chat - no RAG/verse retrieval needed.

    Returns True for greetings, thanks, simple acknowledgments.
    """
    if not message:
        return True  # Treat as casual if empty

    msg = message.lower().strip()

    # Very short messages are usually casual
    word_count = len(msg.split())

    # Single word or very short + matches casual pattern
    if word_count <= 3:
        for pattern in CASUAL_PATTERNS:
            if pattern in msg:
                return True

    # Slightly longer but still casual
    if word_count <= 5:
        for pattern in CASUAL_PATTERNS[:20]:  # Check main casual patterns
            if msg.startswith(pattern) or msg == pattern:
                return True

    return False


def needs_spiritual_context(message: str) -> bool:
    """
    Check if message needs verse/RAG context for a good response.

    Returns True for spiritual questions, life problems, deep queries.
    """
    if not message:
        return False

    msg = message.lower().strip()

    # Check for spiritual/deep patterns first (High priority)
    for pattern in SPIRITUAL_PATTERNS:
        if pattern in msg:
            return True

    # Questions (has ?) with reasonable length likely need context
    # Reduced from 5 words to 3 for shorter questions like "What is my duty?"
    word_count = len(msg.split())
    if "?" in msg and word_count >= 3:
        return True

    # Longer messages (>10 words) that aren't casual likely need context
    if word_count > 10 and not is_casual_message(message):
        return True

    return False


def get_response_template(is_casual: bool) -> str:
    """Get the appropriate response template based on message type."""
    return CASUAL_RESPONSE_TEMPLATE if is_casual else SPIRITUAL_RESPONSE_TEMPLATE
