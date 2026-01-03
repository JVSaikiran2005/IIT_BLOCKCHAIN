/**
 * Authentication Management
 * Handles user registration, login, and token management
 */

// Token storage key
const TOKEN_KEY = 'bond_platform_token';
const USER_KEY = 'bond_platform_user';

// Authentication state
let authToken = null;
let currentUser = null;

// Initialize auth on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAuthState();
    setupAuthUI();
    setupLoginForm();
    setupRegisterForm();
    setupModalHandlers();
});

/**
 * Load authentication state from localStorage
 */
function loadAuthState() {
    const token = localStorage.getItem(TOKEN_KEY);
    const user = localStorage.getItem(USER_KEY);
    
    if (token && user) {
        authToken = token;
        currentUser = JSON.parse(user);
        updateAuthUI();
    }
}

/**
 * Save authentication state to localStorage
 */
function saveAuthState(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    authToken = token;
    currentUser = user;
    updateAuthUI();
}

/**
 * Clear authentication state
 */
function clearAuthState() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    authToken = null;
    currentUser = null;
    updateAuthUI();
}

/**
 * Get current auth token
 */
function getAuthToken() {
    return authToken;
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return authToken !== null && currentUser !== null;
}

/**
 * Get current user
 */
function getCurrentUser() {
    return currentUser;
}

/**
 * Setup authentication UI
 */
function setupAuthUI() {
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const authSection = document.getElementById('authSection');
    const loginSection = document.getElementById('loginSection');
    
    if (loginBtn) {
        loginBtn.addEventListener('click', () => openModal('loginModal'));
    }
    
    if (registerBtn) {
        registerBtn.addEventListener('click', () => openModal('registerModal'));
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    updateAuthUI();
}

/**
 * Update authentication UI based on current state
 */
function updateAuthUI() {
    const authSection = document.getElementById('authSection');
    const loginSection = document.getElementById('loginSection');
    const userInfo = document.getElementById('userInfo');
    
    if (isAuthenticated()) {
        if (authSection) authSection.style.display = 'flex';
        if (loginSection) loginSection.style.display = 'none';
        if (userInfo) userInfo.textContent = `Welcome, ${currentUser.username}`;
    } else {
        if (authSection) authSection.style.display = 'none';
        if (loginSection) loginSection.style.display = 'flex';
    }
}

/**
 * Setup login form
 */
function setupLoginForm() {
    const form = document.getElementById('loginForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const errorDiv = document.getElementById('loginError');
        
        // Clear previous errors
        if (errorDiv) {
            errorDiv.style.display = 'none';
            errorDiv.textContent = '';
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                saveAuthState(data.access_token, {
                    id: data.user_id,
                    username: data.username
                });
                
                closeModal('loginModal');
                form.reset();
                alert('Login successful!');
            } else {
                const error = await response.json();
                if (errorDiv) {
                    errorDiv.textContent = error.detail || 'Login failed';
                    errorDiv.style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Login error:', error);
            if (errorDiv) {
                errorDiv.textContent = 'Failed to connect to server';
                errorDiv.style.display = 'block';
            }
        }
    });
}

/**
 * Setup register form
 */
function setupRegisterForm() {
    const form = document.getElementById('registerForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('registerEmail').value;
        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;
        const passwordConfirm = document.getElementById('registerPasswordConfirm').value;
        const errorDiv = document.getElementById('registerError');
        
        // Clear previous errors
        if (errorDiv) {
            errorDiv.style.display = 'none';
            errorDiv.textContent = '';
        }
        
        // Validate passwords match
        if (password !== passwordConfirm) {
            if (errorDiv) {
                errorDiv.textContent = 'Passwords do not match';
                errorDiv.style.display = 'block';
            }
            return;
        }
        
        // Validate password length
        if (password.length < 6) {
            if (errorDiv) {
                errorDiv.textContent = 'Password must be at least 6 characters';
                errorDiv.style.display = 'block';
            }
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    username: username,
                    password: password
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                saveAuthState(data.access_token, {
                    id: data.user_id,
                    username: data.username
                });
                
                closeModal('registerModal');
                form.reset();
                alert('Registration successful!');
            } else {
                const error = await response.json();
                if (errorDiv) {
                    errorDiv.textContent = error.detail || 'Registration failed';
                    errorDiv.style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Registration error:', error);
            if (errorDiv) {
                errorDiv.textContent = 'Failed to connect to server';
                errorDiv.style.display = 'block';
            }
        }
    });
}

/**
 * Handle logout
 */
function handleLogout() {
    clearAuthState();
    alert('Logged out successfully');
}

/**
 * Setup modal handlers
 */
function setupModalHandlers() {
    // Switch between login and register modals
    const switchToRegister = document.getElementById('switchToRegister');
    const switchToLogin = document.getElementById('switchToLogin');
    
    if (switchToRegister) {
        switchToRegister.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal('loginModal');
            openModal('registerModal');
        });
    }
    
    if (switchToLogin) {
        switchToLogin.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal('registerModal');
            openModal('loginModal');
        });
    }
    
    // Close buttons
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.getAttribute('data-modal');
            if (modalId) {
                closeModal(modalId);
            } else {
                // Fallback for old close buttons
                const modal = btn.closest('.modal');
                if (modal) {
                    modal.style.display = 'none';
                }
            }
        });
    });
    
    // Close on outside click
    window.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

/**
 * Open a modal
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

/**
 * Close a modal
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Make authenticated API request
 */
async function authenticatedFetch(url, options = {}) {
    const token = getAuthToken();
    
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    
    return fetch(url, {
        ...options,
        headers
    });
}

// Export functions for use in other scripts
window.authManager = {
    isAuthenticated,
    getCurrentUser,
    getAuthToken,
    authenticatedFetch,
    handleLogout
};

