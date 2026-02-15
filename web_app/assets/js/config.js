/**
 * API Configuration
 *
 * This file tells the frontend where to find the backend API.
 */

// For development with separate frontend server (VS Code Live Server, etc.)
// point to your local backend server.
// When you deploy and serve frontend from backend, use window.location.origin
(function() {
  const hostname = window.location.hostname;
  const isDev = hostname === 'localhost' || 
                hostname === '127.0.0.1' || 
                hostname.startsWith('192.168.') || 
                hostname.startsWith('10.') ||
                hostname.startsWith('172.');
  
  // In development, backend typically runs on port 8000
  // In production (served by backend), use same origin
  if (isDev && window.location.port === '5500') {
    // VS Code Live Server - point to backend
    window.API_BASE_URL = 'http://localhost:8000';
  } else {
    // Production or served by backend
    window.API_BASE_URL = window.location.origin;
  }
  
  console.log('API_BASE_URL:', window.API_BASE_URL);
})();

