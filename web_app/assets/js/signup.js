// Signup Form Validation and Functionality

document.addEventListener('DOMContentLoaded', function() {
  const signupForm = document.getElementById('signupForm');
  const togglePasswordBtn = document.getElementById('togglePassword');
  const toggleConfirmPasswordBtn = document.getElementById('toggleConfirmPassword');
  const passwordInput = document.getElementById('password');
  const confirmPasswordInput = document.getElementById('confirmPassword');

  // Toggle password visibility
  if (togglePasswordBtn) {
    togglePasswordBtn.addEventListener('click', function(e) {
      e.preventDefault();
      togglePasswordVisibility(passwordInput, togglePasswordBtn);
    });
  }

  if (toggleConfirmPasswordBtn) {
    toggleConfirmPasswordBtn.addEventListener('click', function(e) {
      e.preventDefault();
      togglePasswordVisibility(confirmPasswordInput, toggleConfirmPasswordBtn);
    });
  }

  // Form submission
  if (signupForm) {
    signupForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      if (validateForm()) {
        submitSignupForm();
      }
    });
  }

  // Real-time validation
  const inputs = signupForm.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], input[type="password"]');
  inputs.forEach(input => {
    input.addEventListener('blur', function() {
      validateField(this);
    });

    input.addEventListener('input', function() {
      if (this.parentElement.classList.contains('error')) {
        validateField(this);
      }
    });
  });
});

// Toggle password visibility
function togglePasswordVisibility(inputElement, buttonElement) {
  if (inputElement.type === 'password') {
    inputElement.type = 'text';
    buttonElement.textContent = '🙈';
  } else {
    inputElement.type = 'password';
    buttonElement.textContent = '👁️';
  }
}

// Validate entire form
function validateForm() {
  const firstName = document.getElementById('firstName').value.trim();
  const lastName = document.getElementById('lastName').value.trim();
  const email = document.getElementById('email').value.trim();
  const mobile = document.getElementById('mobile').value.trim();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  const termsCheckbox = document.getElementById('terms');

  let isValid = true;

  // Validate first name
  if (!firstName) {
    showError('firstName', 'First name is required');
    isValid = false;
  } else if (firstName.length < 2) {
    showError('firstName', 'First name must be at least 2 characters');
    isValid = false;
  } else if (!/^[a-zA-Z\s]*$/.test(firstName)) {
    showError('firstName', 'First name can only contain letters');
    isValid = false;
  } else {
    clearError('firstName');
  }

  // Validate last name
  if (!lastName) {
    showError('lastName', 'Last name is required');
    isValid = false;
  } else if (lastName.length < 2) {
    showError('lastName', 'Last name must be at least 2 characters');
    isValid = false;
  } else if (!/^[a-zA-Z\s]*$/.test(lastName)) {
    showError('lastName', 'Last name can only contain letters');
    isValid = false;
  } else {
    clearError('lastName');
  }

  // Validate email
  if (!email) {
    showError('email', 'Email is required');
    isValid = false;
  } else if (!isValidEmail(email)) {
    showError('email', 'Please enter a valid email address');
    isValid = false;
  } else {
    clearError('email');
  }

  // Validate mobile
  if (!mobile) {
    showError('mobile', 'Mobile number is required');
    isValid = false;
  } else if (!/^\d{10}$/.test(mobile)) {
    showError('mobile', 'Mobile number must be 10 digits');
    isValid = false;
  } else {
    clearError('mobile');
  }

  // Validate password
  if (!password) {
    showError('password', 'Password is required');
    isValid = false;
  } else if (!isValidPassword(password)) {
    showError('password', 'Password must be at least 8 characters with uppercase, lowercase, number and special character');
    isValid = false;
  } else {
    clearError('password');
  }

  // Validate confirm password
  if (!confirmPassword) {
    showError('confirmPassword', 'Please confirm your password');
    isValid = false;
  } else if (password !== confirmPassword) {
    showError('confirmPassword', 'Passwords do not match');
    isValid = false;
  } else {
    clearError('confirmPassword');
  }

  // Validate terms checkbox
  if (!termsCheckbox.checked) {
    alert('Please agree to the Terms of Service and Privacy Policy');
    isValid = false;
  }

  return isValid;
}

// Validate individual field
function validateField(field) {
  const fieldName = field.name;
  const value = field.value.trim();

  let isValid = true;
  let errorMessage = '';

  switch (fieldName) {
    case 'firstName':
      if (!value) {
        errorMessage = 'First name is required';
        isValid = false;
      } else if (value.length < 2) {
        errorMessage = 'First name must be at least 2 characters';
        isValid = false;
      } else if (!/^[a-zA-Z\s]*$/.test(value)) {
        errorMessage = 'First name can only contain letters';
        isValid = false;
      }
      break;

    case 'lastName':
      if (!value) {
        errorMessage = 'Last name is required';
        isValid = false;
      } else if (value.length < 2) {
        errorMessage = 'Last name must be at least 2 characters';
        isValid = false;
      } else if (!/^[a-zA-Z\s]*$/.test(value)) {
        errorMessage = 'Last name can only contain letters';
        isValid = false;
      }
      break;

    case 'email':
      if (!value) {
        errorMessage = 'Email is required';
        isValid = false;
      } else if (!isValidEmail(value)) {
        errorMessage = 'Please enter a valid email address';
        isValid = false;
      }
      break;

    case 'mobile':
      if (!value) {
        errorMessage = 'Mobile number is required';
        isValid = false;
      } else if (!/^\d{10}$/.test(value)) {
        errorMessage = 'Mobile number must be 10 digits';
        isValid = false;
      }
      break;

    case 'password':
      if (!value) {
        errorMessage = 'Password is required';
        isValid = false;
      } else if (!isValidPassword(value)) {
        errorMessage = 'Password must be at least 8 characters with uppercase, lowercase, number and special character';
        isValid = false;
      }
      break;

    case 'confirmPassword':
      const password = document.getElementById('password').value;
      if (!value) {
        errorMessage = 'Please confirm your password';
        isValid = false;
      } else if (value !== password) {
        errorMessage = 'Passwords do not match';
        isValid = false;
      }
      break;
  }

  if (isValid) {
    clearError(fieldName);
  } else {
    showError(fieldName, errorMessage);
  }

  return isValid;
}

// Show error message
function showError(fieldName, message) {
  const field = document.getElementById(fieldName);
  const formGroup = field.closest('.form-group');

  formGroup.classList.add('error');
  formGroup.classList.remove('success');

  let errorElement = formGroup.querySelector('.form-error');
  if (!errorElement) {
    errorElement = document.createElement('span');
    errorElement.className = 'form-error';
    formGroup.appendChild(errorElement);
  }
  errorElement.textContent = message;
}

// Clear error message
function clearError(fieldName) {
  const field = document.getElementById(fieldName);
  const formGroup = field.closest('.form-group');

  formGroup.classList.remove('error');
  formGroup.classList.add('success');

  const errorElement = formGroup.querySelector('.form-error');
  if (errorElement) {
    errorElement.remove();
  }
}

// Validate email format
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Validate password strength
function isValidPassword(password) {
  // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  return passwordRegex.test(password);
}

// Submit signup form
function submitSignupForm() {
  const signupBtn = document.querySelector('.signup-btn');
  const originalText = signupBtn.textContent;
  
  signupBtn.disabled = true;
  signupBtn.textContent = 'Creating Account...';

  const formData = {
    firstName: document.getElementById('firstName').value.trim(),
    lastName: document.getElementById('lastName').value.trim(),
    email: document.getElementById('email').value.trim(),
    mobile: document.getElementById('mobile').value.trim(),
    password: document.getElementById('password').value,
  };

  // Simulate API call
  fetch('/api/auth/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData),
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Validate response structure
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid server response format');
      }
      
      // Success
      alert('Account created successfully! Redirecting to login...');
      window.location.href = 'login.html';
    })
    .catch(error => {
      console.error('Signup error:', error);
      const errorMessage = error.message && error.message.includes('HTTP') 
        ? 'Signup failed. Please check your information and try again.' 
        : error.message || 'Signup failed. Please try again.';
      alert(errorMessage);
      signupBtn.disabled = false;
      signupBtn.textContent = originalText;
    });
}

// Google Sign-Up Callback
function handleCredentialResponse(response) {
  console.log('Encoded JWT ID token: ' + response.credential);
  
  // Send token to backend
  fetch('/api/auth/signup/google', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      token: response.credential,
    }),
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Google signup failed');
      }
      return response.json();
    })
    .then(data => {
      // Success
      alert('Account created successfully with Google!');
      window.location.href = 'index.html';
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Google signup failed. Please try again.');
    });
}

// Initialize Google Sign-In
window.onload = function() {
  const googleClientId = 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com';
  
  // Check if Google Client ID is configured
  if (googleClientId.includes('YOUR_GOOGLE_CLIENT_ID')) {
    console.warn('Google Client ID not configured. Google sign-up will be disabled.');
    const googleBtn = document.getElementById('googleSignupBtn');
    if (googleBtn) {
      googleBtn.disabled = true;
      googleBtn.title = 'Google sign-up is not configured';
      googleBtn.textContent = 'Google Sign-Up (Not Configured)';
    }
    return;
  }
  
  try {
    google.accounts.id.initialize({
      client_id: googleClientId,
      callback: handleCredentialResponse,
    });
  } catch (err) {
    console.error('Failed to initialize Google Sign-In:', err);
    const googleBtn = document.getElementById('googleSignupBtn');
    if (googleBtn) {
      googleBtn.disabled = true;
      googleBtn.title = 'Failed to initialize Google sign-up';
    }
  }
};
