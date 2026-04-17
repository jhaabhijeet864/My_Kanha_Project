// History management for chat and search operations
const STORAGE_KEY = 'kanha_history';
const MAX_HISTORY_ITEMS = 50;

/**
 * Save a chat message to history
 * @param {Object} message - Message object with properties: id, text, response, timestamp, type
 */
function saveToHistory(message) {
    try {
        const history = getHistory();
        
        // Add timestamp if not provided
        if (!message.timestamp) {
            message.timestamp = new Date().toISOString();
        }
        
        // Add unique ID if not provided
        if (!message.id) {
            message.id = generateId();
        }
        
        // Add to beginning of history
        history.unshift(message);
        
        // Keep only recent items (limit to MAX_HISTORY_ITEMS)
        if (history.length > MAX_HISTORY_ITEMS) {
            history.pop();
        }
        
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
        console.log('History saved:', message);
        
        return message;
    } catch (error) {
        console.error('Error saving to history:', error);
        return null;
    }
}

/**
 * Get all history items
 * @returns {Array} Array of history items
 */
function getHistory() {
    try {
        const historyData = localStorage.getItem(STORAGE_KEY);
        return historyData ? JSON.parse(historyData) : [];
    } catch (error) {
        console.error('Error retrieving history:', error);
        return [];
    }
}

/**
 * Get history items filtered by type
 * @param {String} type - Type of history (e.g., 'chat', 'search', 'verse')
 * @returns {Array} Filtered history items
 */
function getHistoryByType(type) {
    const history = getHistory();
    return history.filter(item => item.type === type);
}

/**
 * Clear specific history item by ID
 * @param {String} id - ID of the history item to delete
 */
function deleteHistoryItem(id) {
    try {
        const history = getHistory();
        const filtered = history.filter(item => item.id !== id);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
        console.log('History item deleted:', id);
        return true;
    } catch (error) {
        console.error('Error deleting history item:', error);
        return false;
    }
}

/**
 * Clear all history
 */
function clearAllHistory() {
    try {
        localStorage.removeItem(STORAGE_KEY);
        console.log('All history cleared');
        return true;
    } catch (error) {
        console.error('Error clearing history:', error);
        return false;
    }
}

/**
 * Save search query to history
 * @param {String} query - Search query text
 * @param {Array} results - Search results
 */
function saveSearchToHistory(query, results = []) {
    const message = {
        type: 'search',
        text: query,
        results: results,
        resultCount: results.length
    };
    return saveToHistory(message);
}

/**
 * Save chat message to history
 * @param {String} userMessage - User's message
 * @param {String} botResponse - Bot's response
 */
function saveChatToHistory(userMessage, botResponse) {
    const message = {
        type: 'chat',
        text: userMessage,
        response: botResponse
    };
    return saveToHistory(message);
}

/**
 * Save verse view to history
 * @param {Object} verse - Verse object with id, chapter, verse, text
 */
function saveVerseToHistory(verse) {
    const message = {
        type: 'verse',
        text: `Chapter ${verse.chapter}, Verse ${verse.verse}`,
        verse: verse
    };
    return saveToHistory(message);
}

/**
 * Export history as JSON file
 * @param {String} filename - Optional filename for export
 */
function exportHistory(filename = 'kanha_history.json') {
    try {
        const history = getHistory();
        const dataStr = JSON.stringify(history, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        
        URL.revokeObjectURL(url);
        console.log('History exported');
        return true;
    } catch (error) {
        console.error('Error exporting history:', error);
        return false;
    }
}

/**
 * Import history from JSON file
 * @param {File} file - JSON file to import
 */
function importHistory(file) {
    try {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const importedData = JSON.parse(e.target.result);
                
                // Validate imported data is an array
                if (!Array.isArray(importedData)) {
                    console.error('Imported data is not an array');
                    return;
                }
                
                // Validate each history item
                const validatedHistory = importedData.filter((item, index) => {
                    if (!item || typeof item !== 'object') {
                        console.warn(`Skipping invalid item at index ${index}`);
                        return false;
                    }
                    if (!item.role || !item.content) {
                        console.warn(`Skipping item at index ${index}: missing role or content`);
                        return false;
                    }
                    return true;
                });
                
                if (validatedHistory.length === 0) {
                    console.warn('No valid history items found in imported file');
                    return;
                }
                
                const currentHistory = getHistory();
                const mergedHistory = [...validatedHistory, ...currentHistory]
                    .slice(0, MAX_HISTORY_ITEMS);
                localStorage.setItem(STORAGE_KEY, JSON.stringify(mergedHistory));
                console.log(`History imported successfully (${validatedHistory.length} items)`);
            } catch (parseError) {
                console.error('Error parsing imported file:', parseError);
            }
        };
        reader.readAsText(file);
        return true;
    } catch (error) {
        console.error('Error importing history:', error);
        return false;
    }
}

/**
 * Generate unique ID for history items
 * @returns {String} Unique ID
 */
function generateId() {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Get statistics about history
 * @returns {Object} History statistics
 */
function getHistoryStats() {
    const history = getHistory();
    const stats = {
        totalItems: history.length,
        byType: {},
        oldestEntry: history[history.length - 1]?.timestamp || null,
        newestEntry: history[0]?.timestamp || null
    };
    
    history.forEach(item => {
        stats.byType[item.type] = (stats.byType[item.type] || 0) + 1;
    });
    
    return stats;
}
