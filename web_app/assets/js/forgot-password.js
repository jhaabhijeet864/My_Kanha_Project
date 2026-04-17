// Forgot Password Page JavaScript

document.getElementById('resetForm').addEventListener('submit', async function(e) {
  e.preventDefault();

  const email = document.getElementById('email').value;
  const resetBtn = document.querySelector('.login-btn');

  resetBtn.disabled = true;
  const originalText = resetBtn.textContent;
  resetBtn.textContent = 'Sending...';

  try {
    if (!window.Firebase) throw new Error('Firebase not initialized');
    
    await window.Firebase.sendPasswordResetEmail(window.Firebase.auth, email);
    
    // Show success message
    showSuccess('Password reset link sent! Please check your email.');
    resetBtn.textContent = 'Link Sent!';

  } catch (error) {
    console.error('Password reset error:', error);
    showError(error.message || 'Failed to send reset email. Please try again.');
    resetBtn.disabled = false;
    resetBtn.textContent = originalText;
  }
});

function showMessage(message, type = 'error') {
    let msgDiv = document.querySelector('.message-display');
    
    if (!msgDiv) {
        msgDiv = document.createElement('div');
        msgDiv.className = 'message-display';
        const form = document.getElementById('resetForm');
        if (form) {
            form.insertBefore(msgDiv, form.firstChild);
        } else {
            console.error('Reset form not found');
            alert(message); // Fallback to alert
            return;
        }
    }
    
    msgDiv.textContent = message;
    msgDiv.className = `message-display ${type}-message`;
    msgDiv.style.display = 'block';

    if (type === 'error') {
        setTimeout(() => {
            msgDiv.style.display = 'none';
        }, 5000);
    }
}

function showError(message) {
    showMessage(message, 'error');
}

function showSuccess(message) {
    showMessage(message, 'success');
}

// Add some CSS for messages dynamically
const style = document.createElement('style');
style.textContent = `
  .message-display {
    display: none;
    padding: 0.9rem 1rem;
    margin-bottom: 1rem;
    border-radius: 8px;
    font-weight: 500;
    font-size: 0.95rem;
    animation: slideDown 0.3s ease-out;
    text-align: center;
  }
  .error-message {
    background-color: #fee;
    border: 2px solid #f88;
    color: #c33;
  }
  .success-message {
    background-color: #e6ffed;
    border: 2px solid #86e49d;
    color: #0d6a2e;
  }
  
  @keyframes slideDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;
document.head.appendChild(style);
