/**
 * Enhanced Settings Management System
 * Features: Dynamic dark mode, color themes, smooth transitions
 */

class SettingsManager {
    constructor() {
        // In-memory storage (replace with localStorage if available)
        this.settings = {
            darkMode: false,
            colorTheme: 'default',
            language: 'en',
            autoApply: true
        };

        // Enhanced color themes with better contrast
        this.colorThemes = {
            default: {
                name: 'Warm Sunset',
                light: {
                    primary: '#ff9800',
                    secondary: '#ffb74d',
                    accent: '#f57c00',
                    background: '#ffffff',
                    surface: '#f5f5f5',
                    text: '#212121',
                    textSecondary: '#757575',
                    border: '#e0e0e0'
                },
                dark: {
                    primary: '#ffb74d',
                    secondary: '#ffa726',
                    accent: '#ff9800',
                    background: '#0a0a0f',
                    surface: '#1a1a2e',
                    text: '#e0e0e0',
                    textSecondary: '#9e9e9e',
                    border: '#2a2a3e'
                }
            },
            ocean: {
                name: 'Ocean Breeze',
                light: {
                    primary: '#0097a7',
                    secondary: '#26c6da',
                    accent: '#00838f',
                    background: '#ffffff',
                    surface: '#f5f5f5',
                    text: '#212121',
                    textSecondary: '#757575',
                    border: '#e0e0e0'
                },
                dark: {
                    primary: '#26c6da',
                    secondary: '#4dd0e1',
                    accent: '#00acc1',
                    background: '#0a0e12',
                    surface: '#162129',
                    text: '#e0e0e0',
                    textSecondary: '#9e9e9e',
                    border: '#243340'
                }
            },
            purple: {
                name: 'Royal Violet',
                light: {
                    primary: '#7b1fa2',
                    secondary: '#ab47bc',
                    accent: '#6a1b9a',
                    background: '#ffffff',
                    surface: '#f5f5f5',
                    text: '#212121',
                    textSecondary: '#757575',
                    border: '#e0e0e0'
                },
                dark: {
                    primary: '#ba68c8',
                    secondary: '#ce93d8',
                    accent: '#ab47bc',
                    background: '#0f0a12',
                    surface: '#1e162a',
                    text: '#e0e0e0',
                    textSecondary: '#9e9e9e',
                    border: '#2e243a'
                }
            },
            coral: {
                name: 'Vibrant Coral',
                light: {
                    primary: '#e64a19',
                    secondary: '#ff7043',
                    accent: '#d84315',
                    background: '#ffffff',
                    surface: '#f5f5f5',
                    text: '#212121',
                    textSecondary: '#757575',
                    border: '#e0e0e0'
                },
                dark: {
                    primary: '#ff8a65',
                    secondary: '#ffab91',
                    accent: '#ff7043',
                    background: '#120a08',
                    surface: '#2a1612',
                    text: '#e0e0e0',
                    textSecondary: '#9e9e9e',
                    border: '#3a241e'
                }
            },
            rose: {
                name: 'Rose Garden',
                light: {
                    primary: '#c2185b',
                    secondary: '#e91e63',
                    accent: '#ad1457',
                    background: '#ffffff',
                    surface: '#f5f5f5',
                    text: '#212121',
                    textSecondary: '#757575',
                    border: '#e0e0e0'
                },
                dark: {
                    primary: '#f48fb1',
                    secondary: '#f8bbd0',
                    accent: '#ec407a',
                    background: '#120a0f',
                    surface: '#2a1622',
                    text: '#e0e0e0',
                    textSecondary: '#9e9e9e',
                    border: '#3a2632'
                }
            },
            forest: {
                name: 'Forest Green',
                light: {
                    primary: '#388e3c',
                    secondary: '#66bb6a',
                    accent: '#2e7d32',
                    background: '#ffffff',
                    surface: '#f5f5f5',
                    text: '#212121',
                    textSecondary: '#757575',
                    border: '#e0e0e0'
                },
                dark: {
                    primary: '#66bb6a',
                    secondary: '#81c784',
                    accent: '#4caf50',
                    background: '#0a120a',
                    surface: '#162a16',
                    text: '#e0e0e0',
                    textSecondary: '#9e9e9e',
                    border: '#243a24'
                }
            }
        };

        this.initialized = false;
        this.observers = [];
    }

    /**
     * Initialize the settings manager
     */
    init() {
        if (this.initialized) return;

        this.loadSettings();
        this.setupEventListeners();
        this.applyTheme(true);
        this.addStylesheet();
        this.initialized = true;

        console.log('SettingsManager initialized');
    }

    /**
     * Add dynamic stylesheet for transitions
     */
    addStylesheet() {
        if (document.getElementById('settings-dynamic-styles')) return;

        const style = document.createElement('style');
        style.id = 'settings-dynamic-styles';
        style.textContent = `
            /* Smooth transitions for theme changes */
            :root {
                transition: background-color 0.3s ease, color 0.3s ease;
            }

            * {
                transition: background-color 0.3s ease, 
                           color 0.3s ease, 
                           border-color 0.3s ease,
                           box-shadow 0.3s ease;
            }

            /* Dark mode base styles */
            body.dark-mode {
                background-color: var(--bg-color);
                color: var(--text-color);
            }

            /* Notification animations */
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }

            /* Preview box animations */
            .preview-box {
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .preview-box:hover {
                transform: scale(1.05);
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Load settings from storage
     */
    loadSettings() {
        try {
            // Try localStorage first
            if (typeof localStorage !== 'undefined') {
                const saved = localStorage.getItem('kanha_settings');
                if (saved) {
                    this.settings = { ...this.settings, ...JSON.parse(saved) };
                }
            }
        } catch (error) {
            console.warn('localStorage not available, using memory storage');
        }
    }

    /**
     * Save settings to storage
     */
    saveSettings() {
        try {
            if (typeof localStorage !== 'undefined') {
                localStorage.setItem('kanha_settings', JSON.stringify(this.settings));
            }
            this.notifyObservers();
            return true;
        } catch (error) {
            console.warn('Could not save to localStorage:', error);
            return false;
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        const darkModeToggle = document.getElementById('darkMode');
        const colorThemeSelect = document.getElementById('colorTheme');
        const languageSelect = document.getElementById('language');
        const settingsForm = document.querySelector('.settings-form');

        if (darkModeToggle) {
            darkModeToggle.checked = this.settings.darkMode;
            this.updateDarkModeStatus();

            darkModeToggle.addEventListener('change', (e) => {
                this.settings.darkMode = e.target.checked;
                this.updateDarkModeStatus();
                if (this.settings.autoApply) {
                    this.applyTheme();
                    this.saveSettings();
                }
            });
        }

        if (colorThemeSelect) {
            colorThemeSelect.value = this.settings.colorTheme;

            colorThemeSelect.addEventListener('change', (e) => {
                this.settings.colorTheme = e.target.value;
                console.log('Color theme changed to:', e.target.value);
                
                // Force immediate application
                this.applyTheme();
                
                if (this.settings.autoApply) {
                    this.saveSettings();
                }
            });
        }

        if (languageSelect) {
            languageSelect.value = this.settings.language;

            languageSelect.addEventListener('change', (e) => {
                this.settings.language = e.target.value;
                if (this.settings.autoApply) {
                    this.saveSettings();
                }
            });
        }

        if (settingsForm) {
            settingsForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSave();
            });

            settingsForm.addEventListener('reset', (e) => {
                e.preventDefault();
                this.resetToDefaults();
            });
        }

        // Listen for system theme changes
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            darkModeQuery.addEventListener('change', (e) => {
                console.log('System theme changed:', e.matches ? 'dark' : 'light');
            });
        }
    }

    /**
     * Update dark mode status display
     */
    updateDarkModeStatus() {
        const statusText = document.getElementById('darkModeStatus');
        if (statusText) {
            statusText.textContent = this.settings.darkMode ? 'On' : 'Off';
            statusText.style.color = this.settings.darkMode ? '#4caf50' : '#757575';
        }
    }

    /**
     * Apply theme to document
     */
    applyTheme(immediate = false) {
        const theme = this.colorThemes[this.settings.colorTheme] || this.colorThemes.default;
        const palette = this.settings.darkMode ? theme.dark : theme.light;
        const root = document.documentElement;
        const body = document.body;

        // Apply CSS custom properties
        Object.entries(palette).forEach(([key, value]) => {
            const cssVar = `--${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
            root.style.setProperty(cssVar, value);
        });

        // Legacy support for existing code
        root.style.setProperty('--primary-color', palette.primary);
        root.style.setProperty('--secondary-color', palette.secondary);
        root.style.setProperty('--accent-color', palette.accent);
        root.style.setProperty('--bg-color', palette.background);
        root.style.setProperty('--text-color', palette.text);

        // Apply dark mode class
        if (this.settings.darkMode) {
            root.classList.add('dark-mode');
            body.classList.add('dark-mode');
        } else {
            root.classList.remove('dark-mode');
            body.classList.remove('dark-mode');
        }

        // Update meta theme color for mobile browsers
        this.updateMetaThemeColor(palette.primary);

        // Update preview
        this.updatePreview();

        console.log('Theme applied:', this.settings.colorTheme, this.settings.darkMode ? 'dark' : 'light');
    }

    /**
     * Update meta theme color
     */
    updateMetaThemeColor(color) {
        let metaTheme = document.querySelector('meta[name="theme-color"]');
        if (!metaTheme) {
            metaTheme = document.createElement('meta');
            metaTheme.name = 'theme-color';
            document.head.appendChild(metaTheme);
        }
        metaTheme.content = color;
    }

    /**
     * Update theme preview boxes
     */
    updatePreview() {
        const theme = this.colorThemes[this.settings.colorTheme] || this.colorThemes.default;
        const palette = this.settings.darkMode ? theme.dark : theme.light;
        const previewBoxes = document.querySelectorAll('.preview-box');

        if (previewBoxes.length >= 3) {
            previewBoxes[0].style.backgroundColor = palette.primary;
            previewBoxes[1].style.backgroundColor = palette.secondary;
            previewBoxes[2].style.backgroundColor = palette.accent;
            
            // Force repaint
            previewBoxes.forEach(box => {
                box.style.display = 'none';
                box.offsetHeight; // Trigger reflow
                box.style.display = '';
            });
        }

        console.log('Preview updated:', this.settings.colorTheme, palette);
    }

    /**
     * Handle settings save
     */
    handleSave() {
        this.applyTheme();
        
        if (this.saveSettings()) {
            this.showNotification('Settings saved successfully!', 'success');
        } else {
            this.showNotification('Settings saved (session only)', 'warning');
        }
    }

    /**
     * Reset to default settings
     */
    resetToDefaults() {
        this.settings = {
            darkMode: false,
            colorTheme: 'default',
            language: 'en',
            autoApply: true
        };

        // Update form controls
        const darkModeToggle = document.getElementById('darkMode');
        const colorThemeSelect = document.getElementById('colorTheme');
        const languageSelect = document.getElementById('language');

        if (darkModeToggle) {
            darkModeToggle.checked = false;
            this.updateDarkModeStatus();
        }
        if (colorThemeSelect) colorThemeSelect.value = 'default';
        if (languageSelect) languageSelect.value = 'en';

        this.applyTheme();
        this.saveSettings();
        this.showNotification('Settings reset to defaults', 'info');
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const colors = {
            success: '#4caf50',
            error: '#f44336',
            warning: '#ff9800',
            info: '#2196f3'
        };

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
        `;
        
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '16px 24px',
            backgroundColor: colors[type] || colors.info,
            color: 'white',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: '10000',
            animation: 'slideIn 0.3s ease-out',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            fontSize: '14px',
            fontWeight: '500',
            maxWidth: '400px'
        });

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * Get current theme palette
     */
    getCurrentPalette() {
        const theme = this.colorThemes[this.settings.colorTheme] || this.colorThemes.default;
        return this.settings.darkMode ? theme.dark : theme.light;
    }

    /**
     * Toggle dark mode
     */
    toggleDarkMode() {
        this.settings.darkMode = !this.settings.darkMode;
        const toggle = document.getElementById('darkMode');
        if (toggle) toggle.checked = this.settings.darkMode;
        this.updateDarkModeStatus();
        this.applyTheme();
        this.saveSettings();
    }

    /**
     * Set color theme
     */
    setColorTheme(themeName) {
        if (this.colorThemes[themeName]) {
            this.settings.colorTheme = themeName;
            const select = document.getElementById('colorTheme');
            if (select) select.value = themeName;
            this.applyTheme();
            this.saveSettings();
        }
    }

    /**
     * Add observer for settings changes
     */
    addObserver(callback) {
        this.observers.push(callback);
    }

    /**
     * Notify observers of changes
     */
    notifyObservers() {
        this.observers.forEach(callback => callback(this.settings));
    }
}

// Create global instance
const settingsManager = new SettingsManager();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => settingsManager.init());
} else {
    settingsManager.init();
    loadUserProfile();
}

/**
 * Load user profile data and display it
 */
function loadUserProfile() {
    try {
        // Try to get user from localStorage first
        let user = JSON.parse(localStorage.getItem('user') || '{}');
        
        // Get user from Firebase Auth if available
        if (window.firebase && window.firebase.auth) {
            const currentUser = window.firebase.auth().currentUser;
            if (currentUser) {
                user = {
                    name: currentUser.displayName || 'User',
                    email: currentUser.email || 'Not provided',
                    uid: currentUser.uid,
                    avatar: currentUser.photoURL || 'assets/images/default-avatar.png'
                };
            }
        }
        
        // Update profile header
        const profileName = document.getElementById('profileName');
        const profileEmail = document.getElementById('profileEmail');
        const profilePhone = document.getElementById('profilePhone');
        const profileAvatar = document.getElementById('profileAvatar');
        
        if (profileName) profileName.textContent = user.name || 'User';
        if (profileEmail) profileEmail.textContent = user.email || 'Not provided';
        if (profilePhone) profilePhone.textContent = user.phone || 'Not provided';
        if (profileAvatar && user.avatar) profileAvatar.src = user.avatar;
        
        // Update profile details section
        const detailName = document.getElementById('detailName');
        const detailEmail = document.getElementById('detailEmail');
        const detailPhone = document.getElementById('detailPhone');
        const detailJoinDate = document.getElementById('detailJoinDate');
        
        if (detailName) detailName.textContent = user.name || '--';
        if (detailEmail) detailEmail.textContent = user.email || '--';
        if (detailPhone) detailPhone.textContent = user.phone || '--';
        if (detailJoinDate) {
            const joinDate = user.joinDate || new Date().toLocaleDateString();
            detailJoinDate.textContent = joinDate;
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

/**
 * Edit user profile
 */
function editProfile() {
    alert('Edit profile feature coming soon!');
    // TODO: Implement profile edit modal
}

/**
 * Logout user
 */
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        // Clear local storage
        localStorage.removeItem('user');
        localStorage.removeItem('authToken');
        
        // Sign out from Firebase if available
        if (window.firebase && window.firebase.auth) {
            window.firebase.auth().signOut().then(() => {
                window.location.href = 'login.html';
            }).catch((error) => {
                console.error('Logout error:', error);
                window.location.href = 'login.html';
            });
        } else {
            window.location.href = 'login.html';
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = settingsManager;
}

// Make available globally
window.settingsManager = settingsManager;