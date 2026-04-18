// Login Page JavaScript

// Detect if running on mobile device
function isMobileDevice() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Detect if running on localhost/local IP (development mode)
function isLocalDevelopment() {
  const hostname = window.location.hostname;
  return hostname === 'localhost' || 
         hostname === '127.0.0.1' || 
         hostname.startsWith('192.168.') || 
         hostname.startsWith('10.') ||
         hostname.startsWith('172.');
}

// Exchange Firebase ID token with backend and store server JWT
async function exchangeFirebaseToken() {
  try {
    if (!window.Firebase || !window.Firebase.auth) {
      throw new Error('Firebase not initialized');
    }
    const idToken = await window.Firebase.getIdToken();
    if (!idToken) throw new Error('No Firebase ID token');

    const resp = await fetch('/auth/firebase', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: idToken })
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Auth failed' }));
      throw new Error(err.detail || 'Auth failed');
    }
    const data = await resp.json();
    if (data.access_token) {
      localStorage.setItem('authToken', data.access_token);
      if (data.user) localStorage.setItem('user', JSON.stringify(data.user));
      window.location.href = 'chat.html';
    } else {
      throw new Error('Missing access_token in response');
    }
  } catch (e) {
    console.error('Token exchange error:', e);
    showError(e.message || 'Authentication failed');
  }
}

// Handle form submission for email/password login
let loginFormInitialized = false;

function initializeLoginForm() {
  if (loginFormInitialized) return;
  
  const loginForm = document.getElementById('loginForm');
  if (!loginForm) return;
  
  loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const loginBtn = document.querySelector('.login-btn');

    loginBtn.disabled = true;
    const originalText = loginBtn.textContent;
    loginBtn.textContent = 'Signing in...';

    try {
      if (!window.Firebase) throw new Error('Firebase not initialized');
      await window.Firebase.signInWithEmailAndPassword(window.Firebase.auth, email, password);
      await exchangeFirebaseToken();
      document.getElementById('loginForm').reset();
    } catch (error) {
      console.error('Email login error:', error);
      showError(error.message || 'Login failed. Please try again.');
      loginBtn.disabled = false;
      loginBtn.textContent = originalText;
    }
  });
  
  loginFormInitialized = true;
}

// Show error message
function showError(message) {
  // Create error element if it doesn't exist
  let errorDiv = document.querySelector('.error-message');
  
  if (!errorDiv) {
    errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    const form = document.getElementById('loginForm');
    if (form) {
      form.insertBefore(errorDiv, form.firstChild);
    } else {
      console.error('Login form not found');
      alert(message); // Fallback to alert if form doesn't exist
      return;
    }
  }
  
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';
  
  // Auto-hide after 5 seconds
  setTimeout(() => {
    errorDiv.style.display = 'none';
  }, 5000);
}

// Check if already logged in and initialize form when DOM is ready
window.addEventListener('DOMContentLoaded', function() {
  const authToken = localStorage.getItem('authToken');
  if (authToken) {
    // User is already logged in, redirect to chat
    window.location.href = 'chat.html';
    return;
  }

  // Show notice if on local development
  if (isLocalDevelopment()) {
    const notice = document.getElementById('localDevNotice');
    if (notice) {
      notice.style.display = 'block';
    }
  }
  
  // Initialize login form now that DOM is ready
  initializeLoginForm();
});

// Google Sign-In initialization - use the same DOMContentLoaded to avoid double initialization
document.addEventListener('DOMContentLoaded', async function() {
  // Check if returning from a redirect sign-in
  if (window.Firebase && window.Firebase.getRedirectResult) {
    try {
      const result = await window.Firebase.getRedirectResult(window.Firebase.auth);
      if (result && result.user) {
        await exchangeFirebaseToken();
        return;
      }
    } catch (error) {
      if (error.code !== 'auth/no-redirect-user-in-session') {
        console.error('Redirect sign-in error:', error);
      }
    }
  }
});

// Hook Google sign-in button
document.addEventListener('DOMContentLoaded', function() {
  const googleBtn = document.getElementById('googleSignInBtn');
  if (googleBtn) {
    googleBtn.addEventListener('click', async function(e) {
      e.preventDefault();
      
      // Show loading state
      googleBtn.disabled = true;
      googleBtn.innerHTML = '<span style="display:flex;align-items:center;gap:8px;justify-content:center">Signing in...</span>';
      
      try {
        // On mobile or local development, use redirect instead of popup
        // Popup often fails on mobile browsers and local IPs
        if (isMobileDevice() || isLocalDevelopment()) {
          // Use redirect for mobile/local - more reliable
          if (window.Firebase.signInWithRedirect) {
            await window.Firebase.signInWithRedirect(window.Firebase.auth, window.Firebase.googleProvider);
            return; // Page will redirect, then come back
          }
        }
        
        // Desktop with production domain - use popup
        await window.Firebase.signInWithPopup(window.Firebase.auth, window.Firebase.googleProvider);
        await exchangeFirebaseToken();
      } catch (err) {
        console.error('Google sign-in error:', err);
        let errorMessage = 'Google sign-in failed. ';
        
        if (err.code === 'auth/popup-blocked') {
          errorMessage += 'Please allow popups or try email/password login.';
        } else if (err.code === 'auth/unauthorized-domain') {
          errorMessage += 'This domain is not authorized. Please use email/password login on local network.';
        } else if (err.code === 'auth/popup-closed-by-user') {
          errorMessage = 'Sign-in cancelled.';
        } else {
          errorMessage += 'Please try email/password login instead.';
        }
        
        showError(errorMessage);
        googleBtn.disabled = false;
        googleBtn.innerHTML = '<img src="assets/images/icon-192.png" alt="Google" style="width:20px;height:20px;border-radius:4px"> Continue with Google';
      }
    });
  }
});

// Add some CSS for error messages dynamically
const style = document.createElement('style');
style.textContent = `
  .error-message {
    display: none;
    padding: 0.9rem 1rem;
    margin-bottom: 1rem;
    background-color: #fee;
    border: 2px solid #f88;
    border-radius: 8px;
    color: #c33;
    font-weight: 500;
    font-size: 0.95rem;
    animation: slideDown 0.3s ease-out;
  }
  
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;
document.head.appendChild(style);
