/**
 * Bond Investment Platform - Main Application
 * Government Bonds Investment System
 */

const API_URL = 'http://localhost:8000/api';

// State
let selectedBond = null;
let userPortfolio = null;
let authToken = null;

// ====================
// Initialize App
// ====================
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadGovBonds();
    checkAuthStatus();
});

// ====================
// Event Listeners
// ====================
function setupEventListeners() {
    // Auth
    document.getElementById('loginBtn')?.addEventListener('click', () => showModal('loginModal'));
    document.getElementById('registerBtn')?.addEventListener('click', () => showModal('registerModal'));
    document.getElementById('logoutBtn')?.addEventListener('click', logout);
    
    // Navigation
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            target?.scrollIntoView({ behavior: 'smooth' });
        });
    });
    
    // Forms
    document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
    document.getElementById('registerForm')?.addEventListener('submit', handleRegister);
    document.getElementById('investmentForm')?.addEventListener('submit', handleInvestment);
    
    // Modal close
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', e => {
            const modal = e.target.closest('.modal');
            if (modal) modal.style.display = 'none';
        });
    });
    
    // Statistics modal
    document.getElementById('statsModalBtn')?.addEventListener('click', showStatsModal);
    
    // Wallet
    document.getElementById('connectWalletBtn')?.addEventListener('click', connectWallet);
    document.getElementById('disconnectWalletBtn')?.addEventListener('click', disconnectWallet);
}

// ====================
// Load Government Bonds
// ====================
async function loadGovBonds() {
    try {
        const response = await fetch(`${API_URL}/bonds`);
        if (!response.ok) throw new Error('Failed to fetch bonds');
        
        const bonds = await response.json();
        displayGovBonds(bonds);
    } catch (error) {
        console.error('Error loading bonds:', error);
        showError('Failed to load government bonds. Please refresh.');
    } finally {
        // Always hide loading overlay after bonds load
        showLoading(false);
        // Load statistics in background without blocking
        loadStatistics();
    }
}

function displayGovBonds(bonds) {
    const container = document.getElementById('bondsContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (bonds.length === 0) {
        container.innerHTML = '<p class="empty-state">No government bonds available</p>';
        return;
    }
    
    bonds.forEach(bond => {
        const card = createBondCard(bond);
        container.appendChild(card);
    });
}

function createBondCard(bond) {
    const card = document.createElement('div');
    card.className = 'gov-bond-card';
    
    const maturityDate = new Date(bond.maturityDate);
    const daysLeft = Math.ceil((maturityDate - new Date()) / (1000 * 60 * 60 * 24));
    const yearsLeft = (daysLeft / 365).toFixed(1);
    const couponRate = (bond.couponRate / 100).toFixed(2);
    
    card.innerHTML = `
        <div class="bond-header">
            <div class="gov-seal">🏛️</div>
            <div class="bond-title">
                <h3>${bond.name}</h3>
                <p class="issuer">${bond.issuer}</p>
            </div>
        </div>
        
        <p class="description">${bond.description}</p>
        
        <div class="bond-metrics">
            <div class="metric">
                <span class="label">Coupon Rate</span>
                <span class="value highlight">${couponRate}%</span>
            </div>
            <div class="metric">
                <span class="label">Maturity</span>
                <span class="value">${yearsLeft} years</span>
            </div>
            <div class="metric">
                <span class="label">Min. Investment</span>
                <span class="value">$${bond.minimumInvestment}</span>
            </div>
            <div class="metric">
                <span class="label">Face Value</span>
                <span class="value">$${(bond.faceValue / 1000).toFixed(0)}K</span>
            </div>
        </div>
        
        <div class="bond-actions">
            <button class="btn btn-primary" onclick="selectBond(${bond.id})">Invest Now</button>
            <button class="btn btn-secondary" onclick="viewBondDetails(${bond.id})">Details</button>
        </div>
    `;
    
    return card;
}

// ====================
// Bond Selection & Investment
// ====================
async function selectBond(bondId) {
    if (!authToken) {
        alert('Please log in first');
        showModal('loginModal');
        return;
    }
    
    if (!walletManager?.isWalletConnected?.()) {
        alert('Please connect your wallet first');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/bonds/${bondId}`);
        const bond = await response.json();
        selectedBond = bond;
        
        // Populate investment modal
        const detailsDiv = document.getElementById('bondDetails');
        if (detailsDiv) {
            detailsDiv.innerHTML = `
                <div class="selected-bond">
                    <h3>${bond.name}</h3>
                    <p><strong>Issuer:</strong> ${bond.issuer}</p>
                    <p><strong>Coupon Rate:</strong> ${(bond.couponRate / 100).toFixed(2)}%</p>
                    <p><strong>Maturity:</strong> ${new Date(bond.maturityDate).toLocaleDateString()}</p>
                    <p><strong>Minimum Investment:</strong> $${bond.minimumInvestment}</p>
                </div>
            `;
        }
        
        const amountInput = document.getElementById('investmentAmount');
        if (amountInput) {
            amountInput.min = bond.minimumInvestment;
            amountInput.value = bond.minimumInvestment;
        }
        
        showModal('investmentModal');
    } catch (error) {
        console.error('Error loading bond:', error);
        showError('Failed to load bond details');
    }
}

async function viewBondDetails(bondId) {
    try {
        const [bondRes, yieldRes] = await Promise.all([
            fetch(`${API_URL}/bonds/${bondId}`),
            fetch(`${API_URL}/yield/${bondId}`)
        ]);
        
        const bond = await bondRes.json();
        const yieldData = await yieldRes.json();
        
        const details = `
Government Bond: ${bond.name}
Issuer: ${bond.issuer}
Coupon Rate: ${(bond.couponRate / 100).toFixed(2)}%
Current Yield: ${yieldData.currentYield.toFixed(2)}%
Days to Maturity: ${yieldData.daysToMaturity}
Face Value: $${bond.faceValue}
Minimum Investment: $${bond.minimumInvestment}
        `;
        
        alert(details);
    } catch (error) {
        console.error('Error loading bond details:', error);
        showError('Failed to load bond details');
    }
}

// ====================
// Investment
// ====================
async function handleInvestment(e) {
    e.preventDefault();
    
    if (!selectedBond) {
        showError('No bond selected');
        return;
    }
    
    const amount = parseFloat(document.getElementById('investmentAmount').value);
    
    if (isNaN(amount) || amount < selectedBond.minimumInvestment) {
        showError(`Minimum investment is $${selectedBond.minimumInvestment}`);
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_URL}/invest`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                bondId: selectedBond.id,
                investorAddress: walletManager?.getAddress?.() || '0x' + Math.random().toString(16).slice(2),
                amount: amount,
                timestamp: new Date().toISOString(),
                transactionHash: '0x' + Math.random().toString(16).slice(2, 66)
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Investment failed');
        }
        
        const result = await response.json();
        alert(`Investment successful! Amount: $${amount}`);
        
        document.getElementById('investmentForm').reset();
        closeModal('investmentModal');
        loadUserPortfolio();
        loadStatistics();
        loadGovBonds();
    } catch (error) {
        console.error('Investment error:', error);
        showError('Investment failed: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// ====================
// Authentication
// ====================
function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    if (token) {
        authToken = token;
        updateAuthUI(true);
        loadUserPortfolio();
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        if (!response.ok) throw new Error('Login failed');
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        
        updateAuthUI(true);
        closeModal('loginModal');
        loadUserPortfolio();
        
        alert('Login successful!');
    } catch (error) {
        showError('Login failed: ' + error.message);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('registerPasswordConfirm').value;
    
    if (password !== confirmPassword) {
        showError('Passwords do not match');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, username, password })
        });
        
        if (!response.ok) throw new Error('Registration failed');
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        
        updateAuthUI(true);
        closeModal('registerModal');
        
        alert('Registration successful!');
    } catch (error) {
        showError('Registration failed: ' + error.message);
    }
}

function logout() {
    authToken = null;
    localStorage.removeItem('authToken');
    updateAuthUI(false);
    walletManager?.disconnect?.();
    alert('Logged out');
    location.reload();
}

function updateAuthUI(isLoggedIn) {
    const authSection = document.getElementById('authSection');
    const loginSection = document.getElementById('loginSection');
    
    if (authSection) authSection.style.display = isLoggedIn ? 'flex' : 'none';
    if (loginSection) loginSection.style.display = isLoggedIn ? 'none' : 'flex';
}

// ====================
// Portfolio (PRIVATE - Requires Auth)
// ====================
async function loadUserPortfolio() {
    // Only load portfolio if user is authenticated AND wallet is connected
    if (!authToken) {
        showPortfolioMessage('Please log in to view your portfolio', true);
        return;
    }
    
    if (!walletManager?.getAddress?.()) {
        showPortfolioMessage('Please connect your wallet to view your portfolio', true);
        return;
    }
    
    try {
        const address = walletManager.getAddress();
        const response = await fetch(`${API_URL}/portfolio/${address}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                showPortfolioMessage('Unauthorized: Invalid or expired session', true);
            } else {
                showPortfolioMessage('Failed to load portfolio', true);
            }
            return;
        }
        
        userPortfolio = await response.json();
        displayPortfolio(userPortfolio);
    } catch (error) {
        console.error('Error loading portfolio:', error);
        showPortfolioMessage('Error loading portfolio: ' + error.message, true);
    }
}

function showPortfolioMessage(message, isError = false) {
    const container = document.getElementById('portfolioInvestments');
    if (container) {
        const className = isError ? 'empty-state error' : 'empty-state';
        container.innerHTML = `<p class="${className}">${message}</p>`;
    }
}

function displayPortfolio(portfolio) {
    const container = document.getElementById('portfolioInvestments');
    if (!container) return;
    
    if (portfolio.investments.length === 0) {
        container.innerHTML = '<p class="empty-state">No investments yet</p>';
        return;
    }
    
    container.innerHTML = '<h3>Your Investments</h3>';
    
    portfolio.investments.forEach(inv => {
        const item = document.createElement('div');
        item.className = 'investment-item';
        item.innerHTML = `
            <div>
                <strong>Bond ${inv.bondId}</strong>
                <p>${new Date(inv.timestamp).toLocaleDateString()}</p>
            </div>
            <div class="amount">$${inv.amount.toFixed(2)}</div>
        `;
        container.appendChild(item);
    });
    
    // Update stats
    document.getElementById('totalInvested').textContent = '$' + portfolio.totalInvested.toFixed(2);
    document.getElementById('totalValue').textContent = '$' + portfolio.totalValue.toFixed(2);
}

// ====================
// Statistics
// ====================
let statisticsChart = null;

async function loadStatistics() {
    try {
        const response = await fetch(`${API_URL}/investments/stats`);
        if (!response.ok) {
            // Fallback to default values if stats endpoint fails
            displayStatistics({
                totalInvested: 0,
                totalInvestors: 0,
                totalInvestments: 0,
                totalBonds: 11,
                bondStats: {}
            });
            return;
        }
        
        const stats = await response.json();
        displayStatistics(stats);
    } catch (error) {
        console.error('Error loading statistics:', error);
        // Show default stats instead of failing
        displayStatistics({
            totalInvested: 0,
            totalInvestors: 0,
            totalInvestments: 0,
            totalBonds: 11,
            bondStats: {}
        });
    }
}

function displayStatistics(stats) {
    // Update main stats display
    document.getElementById('platformTotalInvested').textContent = '$' + stats.totalInvested.toFixed(2);
    document.getElementById('platformActiveInvestors').textContent = stats.totalInvestors;
    document.getElementById('platformTotalInvestments').textContent = stats.totalInvestments;
    document.getElementById('platformAvailableBonds').textContent = stats.totalBonds;
    
    // Update modal stats display
    document.getElementById('statsDetailTotalInvested').textContent = '$' + stats.totalInvested.toFixed(2);
    document.getElementById('statsDetailActiveInvestors').textContent = stats.totalInvestors;
    document.getElementById('statsDetailTotalInvestments').textContent = stats.totalInvestments;
    document.getElementById('statsDetailAvailableBonds').textContent = stats.totalBonds;
    
    // Store for chart use
    window.currentStats = stats;
    window.bondStats = stats.bondStats || {};
    
    // Display bonds breakdown
    displayBondsBreakdown(stats.bondStats || {});
}

function showStatsModal() {
    const modal = document.getElementById('statsModal');
    if (modal) {
        modal.style.display = 'block';
        // Render chart after modal becomes visible
        setTimeout(() => renderStatisticsChart(), 100);
    }
}

function displayBondsBreakdown(bondStats) {
    const container = document.getElementById('bondsBreakdown');
    if (!container) return;
    
    if (!bondStats || Object.keys(bondStats).length === 0) {
        container.innerHTML = '<p class="empty-state">No investment data yet</p>';
        return;
    }
    
    const sortedBonds = Object.values(bondStats)
        .sort((a, b) => b.totalInvested - a.totalInvested);
    
    let html = '<div class="bonds-table">';
    html += '<div class="table-header">';
    html += '<div class="table-cell">Bond Name</div>';
    html += '<div class="table-cell">Total Invested</div>';
    html += '<div class="table-cell">Investor Count</div>';
    html += '<div class="table-cell">Investments</div>';
    html += '</div>';
    
    sortedBonds.forEach((bond, index) => {
        html += '<div class="table-row ' + (index % 2 === 0 ? 'even' : 'odd') + '">';
        html += '<div class="table-cell"><strong>' + bond.name + '</strong></div>';
        html += '<div class="table-cell">$' + bond.totalInvested.toFixed(2) + '</div>';
        html += '<div class="table-cell"><span class="badge">' + bond.investorCount + '</span></div>';
        html += '<div class="table-cell">' + bond.investmentCount + '</div>';
        html += '</div>';
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function renderStatisticsChart() {
    const stats = window.currentStats || {};
    const bondStats = window.bondStats || {};
    const canvas = document.getElementById('investmentChart');
    
    if (!canvas) return;
    
    // Destroy existing chart if it exists
    if (statisticsChart) {
        statisticsChart.destroy();
    }
    
    // Prepare data for bar chart
    const bondNames = Object.values(bondStats).map(b => b.name.substring(0, 15));
    const investmentAmounts = Object.values(bondStats).map(b => b.totalInvested);
    const investorCounts = Object.values(bondStats).map(b => b.investorCount);
    
    const ctx = canvas.getContext('2d');
    statisticsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: bondNames,
            datasets: [
                {
                    label: 'Total Invested ($)',
                    data: investmentAmounts,
                    backgroundColor: '#4CAF50',
                    borderColor: '#2E7D32',
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'Investor Count',
                    data: investorCounts,
                    backgroundColor: '#2196F3',
                    borderColor: '#1565C0',
                    borderWidth: 1,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 15,
                        font: { size: 13, weight: 'bold' }
                    }
                },
                title: {
                    display: true,
                    text: 'Government Bonds Investment Overview',
                    font: { size: 14, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Amount Invested ($)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Number of Investors'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

// ====================
// Wallet
// ====================
function connectWallet() {
    if (walletManager?.connect) {
        walletManager.connect().then(() => {
            loadUserPortfolio();
        });
    }
}

function disconnectWallet() {
    if (walletManager?.disconnect) {
        walletManager.disconnect();
    }
}

// ====================
// Utilities
// ====================
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'block';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
}

function showError(message) {
    alert(message);
}

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = show ? 'flex' : 'none';
}

// Make functions globally available
window.selectBond = selectBond;
window.viewBondDetails = viewBondDetails;
window.connectWallet = connectWallet;
window.disconnectWallet = disconnectWallet;
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
window.handleInvestment = handleInvestment;
window.logout = logout;
window.showStatsModal = showStatsModal;


