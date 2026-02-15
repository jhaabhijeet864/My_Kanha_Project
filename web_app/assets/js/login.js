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
// Accepts optional user parameter to avoid race condition with auth.currentUser
async function exchangeFirebaseToken(user = null) {
  try {
    if (!window.Firebase || !window.Firebase.auth) {
      throw new Error('Firebase not initialized');
    }
    // Use provided user or wait for auth state to be ready
    const targetUser = user || await window.Firebase.waitForAuthReady();
    if (!targetUser) throw new Error('No authenticated user');
    
    const idToken = await window.Firebase.getIdToken(targetUser);
    if (!idToken) throw new Error('No Firebase ID token');

    const apiUrl = (window.API_BASE_URL || '') + '/auth/firebase';
    const resp = await fetch(apiUrl, {
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

// Show error message
function showError(message) {
  // Create error element
  let errorDiv = document.querySelector('.error-message');
  
  if (!errorDiv) {
    errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    document.querySelector('.login-form').insertBefore(errorDiv, document.querySelector('.form-group'));
  }
  
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';
  
  // Auto-hide after 5 seconds
  setTimeout(() => {
    errorDiv.style.display = 'none';
  }, 5000);
}

// Wait for Firebase module to load (it's loaded as type="module" which defers execution)
function waitForFirebase(timeout = 5000) {
  return new Promise((resolve, reject) => {
    if (window.Firebase) {
      resolve(window.Firebase);
      return;
    }
    const startTime = Date.now();
    const checkInterval = setInterval(() => {
      if (window.Firebase) {
        clearInterval(checkInterval);
        resolve(window.Firebase);
      } else if (Date.now() - startTime > timeout) {
        clearInterval(checkInterval);
        reject(new Error('Firebase initialization timeout'));
      }
    }, 50);
  });
}

// Handle form submission for email/password login
async function handleLoginSubmit(e) {
  e.preventDefault();

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const loginBtn = document.querySelector('.login-btn');

  loginBtn.disabled = true;
  const originalText = loginBtn.textContent;
  loginBtn.textContent = 'Signing in...';

  try {
    const Firebase = await waitForFirebase();
    // Get the user from sign-in result to avoid race condition
    const userCredential = await Firebase.signInWithEmailAndPassword(Firebase.auth, email, password);
    await exchangeFirebaseToken(userCredential.user);
    document.getElementById('loginForm').reset();
  } catch (error) {
    console.error('Email login error:', error);
    showError(error.message || 'Login failed. Please try again.');
    loginBtn.disabled = false;
    loginBtn.textContent = originalText;
  }
}

// Initialize login form when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', handleLoginSubmit);
  }
});

// Check if already logged in
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
});

// Google Sign-In initialization
window.onload = async function() {
  // Wait for Firebase to be ready (loaded as ES module)
  let Firebase;
  try {
    Firebase = await waitForFirebase();
  } catch (err) {
    console.error('Firebase not available:', err);
    showError('Firebase initialization failed. Please refresh the page.');
    return;
  }

  // Check if returning from a redirect sign-in
  if (Firebase.getRedirectResult) {
    try {
      const result = await Firebase.getRedirectResult(Firebase.auth);
      if (result && result.user) {
        await exchangeFirebaseToken(result.user);
        return;
      }
    } catch (err) {
      console.error('Redirect result error:', err);
      // Don't show error here, user might just be loading the page normally
    }
  }

  // Hook Google sign-in button
  const googleBtn = document.getElementById('googleSignInBtn');
  if (googleBtn) {
    googleBtn.addEventListener('click', async function(e) {
      e.preventDefault();
      
      // Show loading state
      googleBtn.disabled = true;
      googleBtn.innerHTML = '<span style="display:flex;align-items:center;gap:8px;justify-content:center">Signing in...</span>';
      
      try {
        const Firebase = await waitForFirebase();
        // On mobile or local development, use redirect instead of popup
        // Popup often fails on mobile browsers and local IPs
        if (isMobileDevice() || isLocalDevelopment()) {
          // Use redirect for mobile/local - more reliable
          if (Firebase.signInWithRedirect) {
            await Firebase.signInWithRedirect(Firebase.auth, Firebase.googleProvider);
            return; // Page will redirect, then come back
          }
        }
        
        // Desktop with production domain - use popup
        const result = await Firebase.signInWithPopup(Firebase.auth, Firebase.googleProvider);
        await exchangeFirebaseToken(result.user);
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
};

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
