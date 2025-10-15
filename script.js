// Xibalba Mixed Media Studio - Client Login System
// Google OAuth Integration for Unified Login

// Google OAuth Configuration
const GOOGLE_CLIENT_ID = 'your-google-client-id.apps.googleusercontent.com';
const GOOGLE_REDIRECT_URI = window.location.origin + '/auth/callback';

// Initialize Google OAuth
function initializeGoogleAuth() {
    // Load Google API
    const script = document.createElement('script');
    script.src = 'https://apis.google.com/js/api.js';
    script.onload = () => {
        gapi.load('auth2', () => {
            gapi.auth2.init({
                client_id: GOOGLE_CLIENT_ID
            });
        });
    };
    document.head.appendChild(script);
}

// Handle Google Login
function handleGoogleLogin() {
    const auth2 = gapi.auth2.getAuthInstance();
    auth2.signIn().then((googleUser) => {
        const profile = googleUser.getBasicProfile();
        const idToken = googleUser.getAuthResponse().id_token;
        
        // Send token to backend for verification
        authenticateUser(idToken, profile);
    }).catch((error) => {
        console.error('Google login failed:', error);
        showError('Login failed. Please try again.');
    });
}

// Authenticate user with backend
async function authenticateUser(idToken, profile) {
    try {
        const response = await fetch('/api/auth/google', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                idToken: idToken,
                email: profile.getEmail(),
                name: profile.getName(),
                imageUrl: profile.getImageUrl()
            })
        });

        if (response.ok) {
            const userData = await response.json();
            handleSuccessfulLogin(userData);
        } else {
            throw new Error('Authentication failed');
        }
    } catch (error) {
        console.error('Authentication error:', error);
        showError('Authentication failed. Please try again.');
    }
}

// Handle successful login
function handleSuccessfulLogin(userData) {
    // Store user data
    localStorage.setItem('user', JSON.stringify(userData));
    
    // Redirect to client dashboard
    window.location.href = '/dashboard';
}

// Show error message
function showError(message) {
    // Create error notification
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #dc3545;
        color: white;
        padding: 1rem;
        border-radius: 4px;
        z-index: 1000;
    `;
    
    document.body.appendChild(errorDiv);
    
    // Remove after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Check if user is already logged in
function checkAuthStatus() {
    const user = localStorage.getItem('user');
    if (user) {
        const userData = JSON.parse(user);
        showUserInfo(userData);
    }
}

// Show user info if logged in
function showUserInfo(userData) {
    const loginSection = document.querySelector('.login');
    if (loginSection) {
        loginSection.innerHTML = `
            <div class="container">
                <h2>Welcome, ${userData.name}!</h2>
                <div class="user-info">
                    <img src="${userData.imageUrl}" alt="Profile" style="width: 50px; height: 50px; border-radius: 50%; margin: 1rem;">
                    <p>Email: ${userData.email}</p>
                    <div class="user-actions">
                        <a href="/dashboard" class="btn btn-primary">Go to Dashboard</a>
                        <button onclick="logout()" class="btn btn-secondary">Logout</button>
                    </div>
                </div>
            </div>
        `;
    }
}

// Logout function
function logout() {
    localStorage.removeItem('user');
    window.location.reload();
}

// Smooth scrolling for navigation links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeGoogleAuth();
    checkAuthStatus();
    initSmoothScrolling();
    
    // Add loading states to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.classList.contains('btn-google')) {
                this.innerHTML = '<span>Logging in...</span>';
                this.disabled = true;
            }
        });
    });
});

// Service worker registration for PWA capabilities
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
