// Simple History Management - Fetches from backend API or localStorage
const LOCAL_CHAT_KEY = 'kanha_chat_history';
const API_BASE_URL = window.API_BASE_URL || window.location.origin;

// Get auth token
function getToken() {
    return localStorage.getItem('authToken') || localStorage.getItem('jwt_token') || null;
}

// Get local chat history (for guest mode)
function getLocalHistory() {
    try {
        return JSON.parse(localStorage.getItem(LOCAL_CHAT_KEY)) || [];
    } catch {
        return [];
    }
}

// Clear local chat history
function clearLocalHistory() {
    localStorage.removeItem(LOCAL_CHAT_KEY);
}

// Fetch history from backend
async function fetchBackendHistory() {
    const token = getToken();
    if (!token) return [];

    try {
        const response = await fetch(`${API_BASE_URL}/api/history/list`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) return [];
        const data = await response.json();
        return data.sessions || [];
    } catch (error) {
        console.error('Error fetching history:', error);
        return [];
    }
}

// Fetch single conversation details
async function fetchConversation(sessionId) {
    const token = getToken();
    if (!token) return null;

    try {
        const response = await fetch(`${API_BASE_URL}/api/history/${sessionId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) return null;
        return await response.json();
    } catch (error) {
        console.error('Error fetching conversation:', error);
        return null;
    }
}

// Delete conversation from backend
async function deleteBackendConversation(sessionId) {
    const token = getToken();
    if (!token) return false;

    try {
        const response = await fetch(`${API_BASE_URL}/api/history/${sessionId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.ok;
    } catch (error) {
        console.error('Error deleting conversation:', error);
        return false;
    }
}

// Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Render history on page
async function renderHistory() {
    const container = document.querySelector('.history-list');
    if (!container) return;

    container.innerHTML = '<p class="history-loading">Loading history...</p>';

    const token = getToken();
    
    // Guest mode - show local history
    if (!token) {
        renderGuestHistory(container);
        return;
    }

    // Logged in - fetch from backend
    const sessions = await fetchBackendHistory();

    if (sessions.length === 0) {
        container.innerHTML = '<p class="history-empty">No history yet. Start chatting!</p>';
        return;
    }

    let html = `<button class="clear-all-btn" onclick="clearAllHistory()">Clear All</button>`;

    for (const session of sessions) {
        const conversation = await fetchConversation(session.session_id);
        if (!conversation || !conversation.messages || conversation.messages.length === 0) continue;

        const firstUserMsg = conversation.messages.find(m => m.role === 'user');
        const firstAssistantMsg = conversation.messages.find(m => m.role === 'assistant');

        html += `
            <div class="history-item" data-session="${session.session_id}">
                <div class="history-item-header">
                    <span>💬 Chat (${conversation.message_count} messages)</span>
                    <button class="delete-btn" onclick="deleteHistoryItem('${session.session_id}')">🗑️</button>
                </div>
                <p><strong>You:</strong> ${escapeHtml(firstUserMsg?.content || 'No message')}</p>
                ${firstAssistantMsg ? `<p class="history-response"><strong>Kanha:</strong> ${escapeHtml(firstAssistantMsg.content.substring(0, 150))}${firstAssistantMsg.content.length > 150 ? '...' : ''}</p>` : ''}
            </div>
        `;
    }

    container.innerHTML = html;
}

// Render guest mode history from localStorage
function renderGuestHistory(container) {
    const messages = getLocalHistory();
    
    if (messages.length === 0) {
        container.innerHTML = '<p class="history-empty">No history yet. Start chatting!</p>';
        return;
    }

    let html = `
        <p class="guest-notice">📌 Guest mode: History is stored locally. <a href="login.html">Login</a> to save your history permanently.</p>
        <button class="clear-all-btn" onclick="clearGuestHistory()">Clear All</button>
    `;

    // Group messages into pairs (user + assistant)
    for (let i = 0; i < messages.length; i += 2) {
        const userMsg = messages[i];
        const assistantMsg = messages[i + 1];
        
        if (!userMsg || userMsg.role !== 'user') continue;

        html += `
            <div class="history-item">
                <div class="history-item-header">
                    <span>💬 Chat</span>
                </div>
                <p><strong>You:</strong> ${escapeHtml(userMsg.content)}</p>
                ${assistantMsg ? `<p class="history-response"><strong>Kanha:</strong> ${escapeHtml(assistantMsg.content.substring(0, 150))}${assistantMsg.content.length > 150 ? '...' : ''}</p>` : ''}
            </div>
        `;
    }

    container.innerHTML = html;
}

// Clear guest history
function clearGuestHistory() {
    if (!confirm('Clear all history? This cannot be undone.')) return;
    clearLocalHistory();
    renderHistory();
}

// Delete single item (backend only)
async function deleteHistoryItem(sessionId) {
    if (!confirm('Delete this conversation?')) return;
    
    const success = await deleteBackendConversation(sessionId);
    if (success) {
        renderHistory();
    } else {
        alert('Failed to delete conversation');
    }
}

// Clear all history (backend)
async function clearAllHistory() {
    if (!confirm('Clear all history? This cannot be undone.')) return;
    
    const sessions = await fetchBackendHistory();
    for (const session of sessions) {
        await deleteBackendConversation(session.session_id);
    }
    renderHistory();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', renderHistory);
