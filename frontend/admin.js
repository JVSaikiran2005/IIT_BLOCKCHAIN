/**
 * Admin Dashboard Module
 * Handles admin login, user management, bonds, payments, and transactions
 */

const ADMIN_API_URL = 'http://localhost:8000/api/admin';
let adminToken = null;
let adminUser = null;
let currentAdminTab = 'users'; // Track current tab

// Initialize admin module
document.addEventListener('DOMContentLoaded', () => {
    setupAdminUI();
});

/**
 * Setup admin UI elements
 */
function setupAdminUI() {
    const adminLoginBtn = document.getElementById('adminLoginBtn');
    if (adminLoginBtn) {
        adminLoginBtn.addEventListener('click', () => {
            showModal('adminLoginModal');
        });
    }

    const adminLoginForm = document.getElementById('adminLoginForm');
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', handleAdminLogin);
    }

    const adminLogoutBtn = document.getElementById('adminLogoutBtn');
    if (adminLogoutBtn) {
        adminLogoutBtn.addEventListener('click', handleAdminLogout);
    }

    // Setup tab buttons
    setupAdminTabs();

    // Load admin state from localStorage
    loadAdminState();
}

/**
 * Setup admin navigation tabs
 */
function setupAdminTabs() {
    const tabButtons = document.querySelectorAll('.admin-tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabName = e.target.getAttribute('data-tab');
            switchAdminTab(tabName);
        });
    });
}

/**
 * Switch admin tabs
 */
function switchAdminTab(tabName) {
    currentAdminTab = tabName;
    
    // Hide all tab contents
    document.querySelectorAll('.admin-tab-content').forEach(content => {
        content.style.display = 'none';
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.admin-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const tabContent = document.getElementById(`admin-${tabName}`);
    if (tabContent) {
        tabContent.style.display = 'block';
    }
    
    // Mark button as active
    const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    // Load data for the tab
    loadAdminTabData(tabName);
}

/**
 * Load data for specific tab
 */
async function loadAdminTabData(tabName) {
    switch(tabName) {
        case 'users':
            loadAdminUsers();
            break;
        case 'bonds':
            loadAdminBonds();
            break;
        case 'payments':
            loadAdminPaymentAccess();
            break;
        case 'transactions':
            loadAdminTransactions();
            break;
        case 'bills':
            loadAdminBills();
            break;
    }
}

/**
 * Load admin state from localStorage
 */
function loadAdminState() {
    const token = localStorage.getItem('adminToken');
    const user = localStorage.getItem('adminUser');
    
    if (token && user) {
        adminToken = token;
        adminUser = JSON.parse(user);
        showAdminDashboard();
    }
}

/**
 * Save admin state to localStorage
 */
function saveAdminState(token, user) {
    localStorage.setItem('adminToken', token);
    localStorage.setItem('adminUser', JSON.stringify(user));
    adminToken = token;
    adminUser = user;
    showAdminDashboard();
}

/**
 * Clear admin state
 */
function clearAdminState() {
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminUser');
    adminToken = null;
    adminUser = null;
    hideAdminDashboard();
}

/**
 * Handle admin login
 */
async function handleAdminLogin(e) {
    e.preventDefault();

    const email = document.getElementById('adminEmail').value.trim();
    const password = document.getElementById('adminPassword').value;
    const errorDiv = document.getElementById('adminLoginError');

    if (!email || !password) {
        if (errorDiv) {
            errorDiv.textContent = 'Please enter email and password';
            errorDiv.style.display = 'block';
        }
        return;
    }

    try {
        const response = await fetch(`${ADMIN_API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Admin login failed');
        }

        const data = await response.json();
        
        saveAdminState(data.access_token, {
            id: data.user_id,
            email: data.email,
            username: data.username
        });

        closeModal('adminLoginModal');
        loadAdminDashboard();
        alert('Admin login successful!');
    } catch (error) {
        console.error('Admin login error:', error);
        if (errorDiv) {
            errorDiv.textContent = error.message;
            errorDiv.style.display = 'block';
        }
    }
}

/**
 * Handle admin logout
 */
function handleAdminLogout() {
    if (confirm('Are you sure you want to logout from admin panel?')) {
        clearAdminState();
        alert('Admin logged out successfully');
        // Reload to reset all state
        location.reload();
    }
}

/**
 * Show admin dashboard
 */
function showAdminDashboard() {
    const adminSection = document.getElementById('admin');
    const adminNavLink = document.getElementById('adminNavLink');
    const loginSection = document.getElementById('loginSection');
    
    if (adminSection) adminSection.style.display = 'block';
    if (adminNavLink) adminNavLink.style.display = 'inline-block';
    if (loginSection) loginSection.style.display = 'none';
    
    // Hide other sections
    document.getElementById('bonds').style.display = 'none';
    document.getElementById('statistics').style.display = 'none';
    document.getElementById('portfolio').style.display = 'none';
    
    // Display admin user info
    const adminUserInfo = document.getElementById('adminUserInfo');
    if (adminUserInfo && adminUser) {
        adminUserInfo.textContent = `Welcome, ${adminUser.email} (Admin)`;
    }
}

/**
 * Hide admin dashboard
 */
function hideAdminDashboard() {
    const adminSection = document.getElementById('admin');
    const adminNavLink = document.getElementById('adminNavLink');
    const loginSection = document.getElementById('loginSection');
    const heroSection = document.getElementById('heroSection');
    
    if (adminSection) adminSection.style.display = 'none';
    if (adminNavLink) adminNavLink.style.display = 'none';
    if (loginSection) loginSection.style.display = 'flex';
    if (heroSection) heroSection.style.display = 'block';
    
    // Show public sections
    if (document.getElementById('bonds')) document.getElementById('bonds').style.display = 'block';
    if (document.getElementById('statistics')) document.getElementById('statistics').style.display = 'block';
    if (document.getElementById('portfolio')) document.getElementById('portfolio').style.display = 'none';
}

/**
 * Load admin dashboard main data
 */
async function loadAdminDashboard() {
    if (!adminToken) {
        hideAdminDashboard();
        return;
    }

    try {
        // Load initial users data
        loadAdminUsers();
    } catch (error) {
        console.error('Error loading admin dashboard:', error);
    }
}

/**
 * Load all users with full data
 */
async function loadAdminUsers() {
    if (!adminToken) return;

    try {
        const response = await fetch(`${ADMIN_API_URL}/users/full`, {
            headers: {
                'Authorization': `Bearer ${adminToken}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                clearAdminState();
                alert('Admin session expired. Please login again.');
                return;
            }
            throw new Error('Failed to load users');
        }

        const data = await response.json();
        displayAdminUsers(data);
    } catch (error) {
        console.error('Error loading users:', error);
        showAdminMessage('users', 'Error loading users: ' + error.message, true);
    }
}

/**
 * Display admin users table
 */
function displayAdminUsers(data) {
    const container = document.getElementById('admin-users');
    if (!container) return;

    if (!data.users || data.users.length === 0) {
        container.innerHTML = '<p class="empty-state">No users registered yet</p>';
        return;
    }

    let html = '<div class="admin-stats">';
    html += '<div class="stat-card"><strong>Total Users:</strong> ' + data.total_users + '</div>';
    html += '</div>';

    html += '<table class="admin-table">';
    html += '<thead><tr>';
    html += '<th>ID</th><th>Email</th><th>Username</th><th>Invested</th>';
    html += '<th>Investments</th><th>Transactions</th><th>Bills</th><th>Actions</th>';
    html += '</tr></thead><tbody>';

    data.users.forEach(user => {
        html += '<tr>';
        html += '<td>' + user.id + '</td>';
        html += '<td>' + user.email + '</td>';
        html += '<td>' + user.username + '</td>';
        html += '<td>$' + user.total_invested.toFixed(2) + '</td>';
        html += '<td>' + user.investment_count + '</td>';
        html += '<td>' + user.transaction_count + '</td>';
        html += '<td>' + user.bill_count + '</td>';
        html += '<td><button class="btn btn-small" onclick="viewUserDetails(' + user.id + ')">View</button></td>';
        html += '</tr>';

        // Credentials row
        html += '<tr class="credential-details">';
        html += '<td colspan="8">';
        html += '<strong>Login Credentials:</strong><br>';
        html += 'Email: ' + user.login_credentials.email + '<br>';
        html += 'Username: ' + user.login_credentials.username + '<br>';
        html += 'Password Hash: <code style="font-size:11px;">' + user.login_credentials.password_hash.substring(0, 50) + '...</code>';
        html += '</td></tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Load all bonds
 */
async function loadAdminBonds() {
    if (!adminToken) return;

    try {
        const response = await fetch(`${ADMIN_API_URL}/bonds`, {
            headers: {
                'Authorization': `Bearer ${adminToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to load bonds');
        
        const data = await response.json();
        displayAdminBonds(data);
    } catch (error) {
        console.error('Error loading bonds:', error);
        showAdminMessage('bonds', 'Error loading bonds: ' + error.message, true);
    }
}

/**
 * Display bonds table
 */
function displayAdminBonds(data) {
    const container = document.getElementById('admin-bonds');
    if (!container) return;

    let html = '<button class="btn btn-primary" onclick="showBondForm()">+ Add New Bond</button>';
    html += '<div id="bondForm" style="display:none;" class="admin-form">';
    html += '<h3>Add New Bond</h3>';
    html += '<form onsubmit="submitAddBond(event)">';
    html += '<input type="text" placeholder="Bond Name" id="bondName" required>';
    html += '<input type="text" placeholder="Issuer" id="bondIssuer" required>';
    html += '<input type="number" placeholder="Face Value" id="bondFaceValue" step="0.01" required>';
    html += '<input type="number" placeholder="Coupon Rate (basis points)" id="bondCouponRate" step="0.01" required>';
    html += '<input type="text" placeholder="Description" id="bondDescription" required>';
    html += '<input type="number" placeholder="Min Investment" id="bondMinInvestment" step="0.01" required>';
    html += '<button type="submit" class="btn btn-primary">Create Bond</button>';
    html += '<button type="button" class="btn btn-secondary" onclick="hideBondForm()">Cancel</button>';
    html += '</form></div>';

    if (!data.bonds || data.bonds.length === 0) {
        html += '<p class="empty-state">No bonds available</p>';
        container.innerHTML = html;
        return;
    }

    html += '<table class="admin-table">';
    html += '<thead><tr>';
    html += '<th>ID</th><th>Name</th><th>Issuer</th><th>Coupon Rate</th>';
    html += '<th>Face Value</th><th>Min Investment</th><th>Maturity</th><th>Actions</th>';
    html += '</tr></thead><tbody>';

    data.bonds.forEach(bond => {
        const coupon = (bond.couponRate / 100).toFixed(2);
        const maturity = new Date(bond.maturityDate).toLocaleDateString();
        
        html += '<tr>';
        html += '<td>' + bond.id + '</td>';
        html += '<td>' + bond.name + '</td>';
        html += '<td>' + bond.issuer + '</td>';
        html += '<td>' + coupon + '%</td>';
        html += '<td>$' + bond.faceValue.toFixed(2) + '</td>';
        html += '<td>$' + bond.minimumInvestment.toFixed(2) + '</td>';
        html += '<td>' + maturity + '</td>';
        html += '<td>';
        html += '<button class="btn btn-small" onclick="editBond(' + bond.id + ')">Edit</button> ';
        html += '<button class="btn btn-danger btn-small" onclick="deleteBond(' + bond.id + ')">Delete</button>';
        html += '</td></tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Show bond form
 */
function showBondForm() {
    const form = document.getElementById('bondForm');
    if (form) form.style.display = 'block';
}

/**
 * Hide bond form
 */
function hideBondForm() {
    const form = document.getElementById('bondForm');
    if (form) form.style.display = 'none';
}

/**
 * Submit add bond form
 */
async function submitAddBond(e) {
    e.preventDefault();

    const bondData = {
        id: Date.now(),
        name: document.getElementById('bondName').value,
        issuer: document.getElementById('bondIssuer').value,
        faceValue: parseFloat(document.getElementById('bondFaceValue').value),
        couponRate: parseFloat(document.getElementById('bondCouponRate').value),
        description: document.getElementById('bondDescription').value,
        minimumInvestment: parseFloat(document.getElementById('bondMinInvestment').value),
        maturityDate: new Date(Date.now() + 365*24*60*60*1000).toISOString(),
        issueDate: new Date().toISOString(),
        bondTokenAddress: '0x' + Math.random().toString(16).slice(2, 42)
    };

    try {
        const response = await fetch(`${ADMIN_API_URL}/bonds`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken}`
            },
            body: JSON.stringify(bondData)
        });

        if (!response.ok) throw new Error('Failed to create bond');

        alert('Bond created successfully!');
        document.getElementById('bondName').value = '';
        document.getElementById('bondIssuer').value = '';
        hideBondForm();
        loadAdminBonds();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

/**
 * Delete bond
 */
async function deleteBond(bondId) {
    if (!confirm('Are you sure you want to delete this bond?')) return;

    try {
        const response = await fetch(`${ADMIN_API_URL}/bonds/${bondId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${adminToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to delete bond');

        alert('Bond deleted successfully!');
        loadAdminBonds();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

/**
 * Load payment access
 */
async function loadAdminPaymentAccess() {
    if (!adminToken) return;

    try {
        const response = await fetch(`${ADMIN_API_URL}/payment-access`, {
            headers: {
                'Authorization': `Bearer ${adminToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to load payment access');

        const data = await response.json();
        displayPaymentAccess(data);
    } catch (error) {
        console.error('Error loading payment access:', error);
        showAdminMessage('payments', 'Error loading payment access: ' + error.message, true);
    }
}

/**
 * Display payment access table
 */
function displayPaymentAccess(data) {
    const container = document.getElementById('admin-payments');
    if (!container) return;

    if (!data.payment_access || data.payment_access.length === 0) {
        container.innerHTML = '<p class="empty-state">No payment access records</p>';
        return;
    }

    let html = '<table class="admin-table">';
    html += '<thead><tr>';
    html += '<th>User ID</th><th>Username</th><th>Email</th><th>Access Level</th>';
    html += '<th>Can Invest</th><th>Can Withdraw</th><th>Can Transfer</th>';
    html += '<th>Status</th><th>Actions</th>';
    html += '</tr></thead><tbody>';

    data.payment_access.forEach(access => {
        html += '<tr>';
        html += '<td>' + access.user_id + '</td>';
        html += '<td>' + access.username + '</td>';
        html += '<td>' + access.email + '</td>';
        html += '<td>' + access.access_level + '</td>';
        html += '<td>' + (access.can_invest ? '✓' : '✗') + '</td>';
        html += '<td>' + (access.can_withdraw ? '✓' : '✗') + '</td>';
        html += '<td>' + (access.can_transfer ? '✓' : '✗') + '</td>';
        html += '<td><span class="badge ' + (access.payment_status === 'active' ? 'active' : 'blocked') + '">' + access.payment_status + '</span></td>';
        html += '<td><button class="btn btn-small" onclick="editPaymentAccess(' + access.user_id + ')">Edit</button></td>';
        html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Load transactions
 */
async function loadAdminTransactions() {
    if (!adminToken) return;

    try {
        const response = await fetch(`${ADMIN_API_URL}/transactions`, {
            headers: {
                'Authorization': `Bearer ${adminToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to load transactions');

        const data = await response.json();
        displayAdminTransactions(data);
    } catch (error) {
        console.error('Error loading transactions:', error);
        showAdminMessage('transactions', 'Error loading transactions: ' + error.message, true);
    }
}

/**
 * Display transactions table
 */
function displayAdminTransactions(data) {
    const container = document.getElementById('admin-transactions');
    if (!container) return;

    if (!data.transactions || data.transactions.length === 0) {
        container.innerHTML = '<p class="empty-state">No transactions recorded</p>';
        return;
    }

    let html = '<div class="admin-stats">';
    html += '<div class="stat-card"><strong>Total Transactions:</strong> ' + data.total_transactions + '</div>';
    html += '</div>';

    html += '<table class="admin-table">';
    html += '<thead><tr>';
    html += '<th>ID</th><th>User</th><th>Type</th><th>Amount</th><th>Status</th><th>Date</th>';
    html += '</tr></thead><tbody>';

    data.transactions.forEach(trans => {
        const date = new Date(trans.created_at).toLocaleDateString();
        html += '<tr>';
        html += '<td>' + trans.id + '</td>';
        html += '<td>' + trans.username + ' (' + trans.email + ')</td>';
        html += '<td>' + trans.type + '</td>';
        html += '<td>$' + trans.amount.toFixed(2) + '</td>';
        html += '<td><span class="badge ' + trans.status + '">' + trans.status + '</span></td>';
        html += '<td>' + date + '</td></tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Load bills
 */
async function loadAdminBills() {
    if (!adminToken) return;

    try {
        const response = await fetch(`${ADMIN_API_URL}/bills`, {
            headers: {
                'Authorization': `Bearer ${adminToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to load bills');

        const data = await response.json();
        displayAdminBills(data);
    } catch (error) {
        console.error('Error loading bills:', error);
        showAdminMessage('bills', 'Error loading bills: ' + error.message, true);
    }
}

/**
 * Display bills table
 */
function displayAdminBills(data) {
    const container = document.getElementById('admin-bills');
    if (!container) return;

    if (!data.bills || data.bills.length === 0) {
        container.innerHTML = '<p class="empty-state">No bills generated</p>';
        return;
    }

    let html = '<div class="admin-stats">';
    html += '<div class="stat-card"><strong>Total Amount:</strong> $' + data.summary.total_amount.toFixed(2) + '</div>';
    html += '<div class="stat-card"><strong>Total Tax:</strong> $' + data.summary.total_tax.toFixed(2) + '</div>';
    html += '<div class="stat-card"><strong>Total Fee:</strong> $' + data.summary.total_fee.toFixed(2) + '</div>';
    html += '<div class="stat-card"><strong>Net Amount:</strong> $' + data.summary.total_net.toFixed(2) + '</div>';
    html += '</div>';

    html += '<table class="admin-table">';
    html += '<thead><tr>';
    html += '<th>ID</th><th>User</th><th>Bond</th><th>Amount</th><th>Tax</th><th>Fee</th><th>Net</th><th>Status</th><th>Date</th>';
    html += '</tr></thead><tbody>';

    data.bills.forEach(bill => {
        const date = new Date(bill.created_at).toLocaleDateString();
        html += '<tr>';
        html += '<td>' + bill.id + '</td>';
        html += '<td>' + bill.username + '</td>';
        html += '<td>' + (bill.bond_name || 'N/A') + '</td>';
        html += '<td>$' + bill.amount.toFixed(2) + '</td>';
        html += '<td>$' + bill.tax_amount.toFixed(2) + '</td>';
        html += '<td>$' + bill.fee_amount.toFixed(2) + '</td>';
        html += '<td>$' + bill.net_amount.toFixed(2) + '</td>';
        html += '<td><span class="badge ' + bill.status + '">' + bill.status + '</span></td>';
        html += '<td>' + date + '</td></tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Show admin message
 */
function showAdminMessage(tabName, message, isError = false) {
    const container = document.getElementById(`admin-${tabName}`);
    if (container) {
        const className = isError ? 'empty-state error' : 'empty-state';
        container.innerHTML = `<p class="${className}">${message}</p>`;
    }
}

/**
 * Utility functions
 */
function viewUserDetails(userId) {
    alert('View details for user ' + userId + ' - Feature coming soon');
}

function editBond(bondId) {
    const container = document.getElementById('admin-bonds');
    if (!container) return;
    const rows = container.querySelectorAll('table tbody tr');
    let bond = null;
    rows.forEach(row => {
        const id = parseInt(row.cells[0].textContent);
        if (id === bondId) {
            bond = { id: bondId, name: row.cells[1].textContent, issuer: row.cells[2].textContent };
        }
    });
    if (!bond) return;
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'editBondModal';
    modal.innerHTML = `<div class="modal-content modal-medium"><span class="close" onclick="closeEditBondModal()">&times;</span><h2>Edit Bond Name</h2><form onsubmit="submitEditBond(event, ${bondId})" class="admin-form"><div class="form-group"><label>Bond ID: ${bondId}</label></div><div class="form-group"><label>Current Name</label><input type="text" id="editBondCurrentName" value="${bond.name}" readonly class="readonly-input"></div><div class="form-group"><label>New Bond Name</label><input type="text" id="editBondNewName" placeholder="Enter new bond name" required></div><div class="form-actions"><button type="submit" class="btn btn-primary">Update Bond Name</button><button type="button" class="btn btn-secondary" onclick="closeEditBondModal()">Cancel</button></div></form></div>`;
    document.body.appendChild(modal);
    modal.style.display = 'block';
    modal.onclick = function(event) { if (event.target === modal) closeEditBondModal(); };
}

function closeEditBondModal() {
    const modal = document.getElementById('editBondModal');
    if (modal) modal.remove();
}

async function submitEditBond(event, bondId) {
    event.preventDefault();
    const newName = document.getElementById('editBondNewName').value.trim();
    if (!newName) {
        alert('Please enter a new bond name');
        return;
    }
    try {
        const response = await fetch(`${ADMIN_API_URL}/bonds/${bondId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken}`
            },
            body: JSON.stringify({ name: newName })
        });
        if (!response.ok) throw new Error('Failed to update bond');
        alert('Bond name updated successfully!');
        closeEditBondModal();
        loadAdminBonds();
    } catch (error) {
        console.error('Error updating bond:', error);
        alert('Error: ' + error.message);
    }
}

function viewUserDetails(userId) {
    const container = document.getElementById('admin-users');
    if (!container) return;
    const rows = container.querySelectorAll('table tbody tr');
    let user = null;
    rows.forEach(row => {
        const id = parseInt(row.cells[0].textContent);
        if (id === userId) {
            user = { id: userId, email: row.cells[1].textContent, username: row.cells[2].textContent };
        }
    });
    if (!user) return;
    fetchAndShowUserDetails(userId, user);
}

async function fetchAndShowUserDetails(userId, basicUser) {
    if (!adminToken) return;
    try {
        const response = await fetch(`${ADMIN_API_URL}/users/full`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        if (!response.ok) throw new Error('Failed to fetch user details');
        const data = await response.json();
        const fullUser = data.users.find(u => u.id === userId);
        if (!fullUser) {
            alert('User details not found');
            return;
        }
        displayUserDetailsModal(fullUser);
    } catch (error) {
        console.error('Error fetching user details:', error);
        alert('Error: ' + error.message);
    }
}

function displayUserDetailsModal(user) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'userDetailsModal';
    const paymentStatus = user.payment_access ? user.payment_access.status || 'not_configured' : 'not_configured';
    modal.innerHTML = `<div class="modal-content modal-large"><span class="close" onclick="closeUserDetailsModal()">&times;</span><h2>User Full Details - ${user.username}</h2><div class="details-section"><h3>Basic Information</h3><div class="details-grid"><div class="detail-item"><label>User ID</label><span>${user.id}</span></div><div class="detail-item"><label>Username</label><span>${user.username}</span></div><div class="detail-item"><label>Email</label><span>${user.email}</span></div><div class="detail-item"><label>Account Created</label><span>${new Date(user.created_at).toLocaleDateString()}</span></div></div></div><div class="details-section"><h3>Login Credentials</h3><div class="details-grid"><div class="detail-item full-width"><label>Email Address</label><input type="text" value="${user.login_credentials.email}" readonly class="readonly-input"></div><div class="detail-item full-width"><label>Username</label><input type="text" value="${user.login_credentials.username}" readonly class="readonly-input"></div><div class="detail-item full-width"><label>Password Hash</label><input type="text" value="${user.login_credentials.password_hash}" readonly class="readonly-input" style="font-size: 11px;"></div></div></div><div class="details-section"><h3>Investment Summary</h3><div class="details-grid"><div class="detail-item"><label>Total Invested</label><span class="highlight">$${user.total_invested.toFixed(2)}</span></div><div class="detail-item"><label>Active Investments</label><span class="highlight">${user.investment_count}</span></div><div class="detail-item"><label>Transactions</label><span>${user.transaction_count}</span></div><div class="detail-item"><label>Bills</label><span>${user.bill_count}</span></div></div></div><div class="details-section"><h3>Payment Access</h3><div class="details-grid"><div class="detail-item full-width"><label>Payment Status</label><span class="status-badge status-${paymentStatus.replace(/_/g, '-')}">${paymentStatus.toUpperCase().replace(/_/g, ' ')}</span></div></div></div><div class="form-actions" style="margin-top: 20px;"><button type="button" class="btn btn-secondary" onclick="closeUserDetailsModal()">Close</button></div></div>`;
    document.body.appendChild(modal);
    modal.style.display = 'block';
    modal.onclick = function(event) { if (event.target === modal) closeUserDetailsModal(); };
}

function closeUserDetailsModal() {
    const modal = document.getElementById('userDetailsModal');
    if (modal) modal.remove();
}

function editPaymentAccess(userId) {
    alert('Edit payment access for user ' + userId + ' - Feature coming soon');
}

// Make functions globally available
window.loadAdminDashboard = loadAdminDashboard;
window.handleAdminLogin = handleAdminLogin;
window.handleAdminLogout = handleAdminLogout;
window.switchAdminTab = switchAdminTab;
window.showBondForm = showBondForm;
window.hideBondForm = hideBondForm;
window.submitAddBond = submitAddBond;
window.deleteBond = deleteBond;
window.viewUserDetails = viewUserDetails;
window.editBond = editBond;
window.closeEditBondModal = closeEditBondModal;
window.submitEditBond = submitEditBond;
window.fetchAndShowUserDetails = fetchAndShowUserDetails;
window.displayUserDetailsModal = displayUserDetailsModal;
window.closeUserDetailsModal = closeUserDetailsModal;
window.editPaymentAccess = editPaymentAccess;
