/**
 * Chat functionality for My Kanha Web App
 * Handles user messages, Krishna responses, and verse citations
 */

// Chat state
const chatState = {
    isLoading: false,
    conversationHistory: [],
    language: 'english'
};

// DOM Elements (initialized on DOMContentLoaded)
let chatWindow;
let chatForm;
let chatInput;
let sendBtn;

/**
 * Initialize chat functionality
 */
function initChat() {
    // Get DOM elements
    chatWindow = document.querySelector('.chat-window');
    chatForm = document.querySelector('.chat-form');
    chatInput = document.querySelector('.chat-input');
    sendBtn = document.querySelector('.send-btn');

    if (!chatForm || !chatInput || !sendBtn) {
        console.error('Chat elements not found!');
        return;
    }

    // Enable inputs
    chatInput.disabled = false;
    sendBtn.disabled = false;
    chatInput.placeholder = 'Ask Krishna anything...';

    // Add event listeners
    chatForm.addEventListener('submit', handleSubmit);
    chatInput.addEventListener('keydown', handleKeyDown);

    // Load conversation history
    loadConversationHistory();

    // Check backend health
    checkBackendStatus();

    // Show welcome message if no history
    if (chatState.conversationHistory.length === 0) {
        showWelcomeMessage();
    }

    // Focus input
    chatInput.focus();
}

/**
 * Check if backend is available
 */
async function checkBackendStatus() {
    try {
        const isReachable = await kanhaAPI.isBackendReachable();
        if (!isReachable) {
            showSystemMessage('Backend server not reachable. Please start the server at localhost:8000', 'error');
        }
    } catch (error) {
        console.error('Backend check failed:', error);
    }
}

/**
 * Show welcome message
 */
function showWelcomeMessage() {
const welcomeHtml = `
    <div class="message krishna-message welcome-message">
        <div class="message-avatar">
            <img src="assets/images/k.ico" alt="Krishna" class="avatar-img">
        </div>
        <div class="message-content">
            <div class="message-text">
                Namaste, dear seeker! I am here to share the eternal wisdom of the Bhagavad Gita.
                Ask me anything about life, duty, purpose, or spiritual growth.
            </div>
            <div class="message-time">${getCurrentTime()}</div>
        </div>
    </div>
`;  
  chatWindow.insertAdjacentHTML('beforeend', welcomeHtml);
}

/**
 * Handle example prompt clicks
 * @param {Event} e - Click event
 * @param {string} prompt - The example question
 */
function askExample(e, prompt) {
    e.preventDefault();
    chatInput.value = prompt;
    chatForm.dispatchEvent(new Event('submit'));
}

/**
 * Handle form submission
 * @param {Event} e - Submit event
 */
async function handleSubmit(e) {
    e.preventDefault();

    const message = chatInput.value.trim();
    if (!message || chatState.isLoading) return;

    // Clear input and disable while processing
    chatInput.value = '';
    setLoading(true);

    // Add user message to chat
    addUserMessage(message);

    // Detect language
    const detectedLang = isHindiText(message) ? 'hindi' : 'english';

    try {
        // Send to backend
        const response = await kanhaAPI.sendMessage(
            message,
            detectedLang,
            5,
            getRecentHistory()
        );

        // Add Krishna's response
        addKrishnaMessage(response.response, response.sources);

        // Update conversation history
        updateConversationHistory(message, response.response);

    } catch (error) {
        console.error('Chat error:', error);
        showSystemMessage(`Error: ${error.message}. Please check if the backend is running.`, 'error');
    } finally {
        setLoading(false);
        chatInput.focus();
    }
}

/**
 * Handle keyboard shortcuts
 * @param {KeyboardEvent} e - Keyboard event
 */
function handleKeyDown(e) {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
}

/**
 * Set loading state
 * @param {boolean} loading - Loading state
 */
function setLoading(loading) {
    chatState.isLoading = loading;
    chatInput.disabled = loading;
    sendBtn.disabled = loading;

    if (loading) {
        sendBtn.textContent = '...';
        showTypingIndicator();
    } else {
        sendBtn.textContent = 'Send';
        hideTypingIndicator();
    }
}

/**
 * Add user message to chat window
 * @param {string} message - User's message
 */
function addUserMessage(message) {
    const messageHtml = `
    <div class="message user-message">
        <div class="message-content">
            <div class="message-text">${escapeHtml(message)}</div>
            <div class="message-time">${getCurrentTime()}</div>
        </div>
        <div class="message-avatar">👤</div>
    </div>
`;
    chatWindow.insertAdjacentHTML('beforeend', messageHtml);
    scrollToBottom(chatWindow);
}

/**
 * Add Krishna's response to chat window
 * @param {string} response - Krishna's response text
 * @param {Array} sources - Verse sources
 */
function addKrishnaMessage(response, sources = []) {
    let sourcesHtml = '';

    if (sources && sources.length > 0) {
        sourcesHtml = `
            <div class="message-sources">
                <div class="sources-header">📖 Referenced Verses:</div>
                ${sources.map(source => `
                    <div class="source-item">
                        <div class="source-reference">${formatVerseCitation(source)}</div>
                        ${source.sanskrit ? `<div class="source-sanskrit">${source.sanskrit}</div>` : ''}
                        <div class="source-translation">${source.english || source.hindi || ''}</div>
                        ${source.similarity_score ? `<div class="source-relevance">${formatSimilarityScore(source.similarity_score)}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

const messageHtml = `
    <div class="message krishna-message">
        <div class="message-avatar">
            <img src="assets/images/k.ico" alt="Krishna" class="avatar-img">
        </div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(response)}</div>
            ${sourcesHtml}
            <div class="message-time">${getCurrentTime()}</div>
        </div>
    </div>
`;

    chatWindow.insertAdjacentHTML('beforeend', messageHtml);
    scrollToBottom(chatWindow);
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    const existingIndicator = document.querySelector('.typing-indicator');
    if (existingIndicator) return;

const indicatorHtml = `
    <div class="message krishna-message typing-indicator">
        <div class="message-avatar">
            <img src="assets/images/k.ico" alt="Krishna" class="avatar-img">
        </div>
        <div class="message-content">
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    </div>
`;
    chatWindow.insertAdjacentHTML('beforeend', indicatorHtml);
    scrollToBottom(chatWindow);
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    const indicator = document.querySelector('.typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Show system message (errors, info)
 * @param {string} message - Message text
 * @param {string} type - Message type ('info', 'error', 'success')
 */
function showSystemMessage(message, type = 'info') {
    const messageHtml = `
        <div class="message system-message ${type}">
            <div class="message-content">
                <div class="message-text">${escapeHtml(message)}</div>
            </div>
        </div>
    `;
    chatWindow.insertAdjacentHTML('beforeend', messageHtml);
    scrollToBottom(chatWindow);
}

/**
 * Get recent conversation history for context
 * @returns {Array} - Recent messages
 */
function getRecentHistory() {
    return chatState.conversationHistory.slice(-6).map(msg => ({
        role: msg.role,
        content: msg.content
    }));
}

/**
 * Update conversation history
 * @param {string} userMessage - User's message
 * @param {string} assistantResponse - Krishna's response
 */
function updateConversationHistory(userMessage, assistantResponse) {
    chatState.conversationHistory.push(
        { role: 'user', content: userMessage },
        { role: 'assistant', content: assistantResponse }
    );

    // Keep only last 20 messages
    if (chatState.conversationHistory.length > 20) {
        chatState.conversationHistory = chatState.conversationHistory.slice(-20);
    }

    // Save to localStorage
    saveConversationHistory();
}

/**
 * Save conversation history to localStorage
 */
function saveConversationHistory() {
    storeLocal('kanha_chat_history', chatState.conversationHistory);
}

/**
 * Load conversation history from localStorage
 */
function loadConversationHistory() {
    const history = getLocal('kanha_chat_history', []);
    chatState.conversationHistory = history;

    // Render previous messages
    history.forEach((msg, index) => {
        if (msg.role === 'user') {
            addUserMessage(msg.content);
        } else if (msg.role === 'assistant') {
            // For loaded history, don't show sources (we don't have them stored)
            addKrishnaMessage(msg.content, []);
        }
    });
}


// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initChat);
