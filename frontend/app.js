/**
 * Main Application Logic
 * Handles bond browsing, investment, and portfolio management
 */

const API_BASE_URL = 'http://localhost:8000/api';

let currentBondId = null;
let yieldChart = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadBonds();
    loadPortfolio();
    setupModal();
    setupInvestmentForm();
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

/**
 * Load all available bonds
 */
async function loadBonds() {
    try {
        const response = await fetch(`${API_BASE_URL}/bonds`);
        const bonds = await response.json();
        
        const container = document.getElementById('bondsContainer');
        container.innerHTML = '';
        
        bonds.forEach(bond => {
            const bondCard = createBondCard(bond);
            container.appendChild(bondCard);
        });
    } catch (error) {
        console.error('Error loading bonds:', error);
        document.getElementById('bondsContainer').innerHTML = 
            '<p class="empty-state">Failed to load bonds. Please check if the backend is running.</p>';
    }
}

/**
 * Create a bond card element
 */
function createBondCard(bond) {
    const card = document.createElement('div');
    card.className = 'bond-card';
    
    // Calculate days to maturity
    const maturityDate = new Date(bond.maturityDate);
    const daysToMaturity = Math.ceil((maturityDate - new Date()) / (1000 * 60 * 60 * 24));
    const yearsToMaturity = (daysToMaturity / 365).toFixed(1);
    
    // Format coupon rate
    const couponRate = (bond.couponRate / 100).toFixed(2);
    
    card.innerHTML = `
        <div class="bond-header">
            <div>
                <div class="bond-name">${bond.name}</div>
                <div class="bond-issuer">${bond.issuer}</div>
            </div>
        </div>
        <div class="bond-description">${bond.description}</div>
        <div class="bond-details">
            <div class="bond-detail-item">
                <div class="bond-detail-label">Coupon Rate</div>
                <div class="bond-detail-value highlight">${couponRate}%</div>
            </div>
            <div class="bond-detail-item">
                <div class="bond-detail-label">Maturity</div>
                <div class="bond-detail-value">${yearsToMaturity} years</div>
            </div>
            <div class="bond-detail-item">
                <div class="bond-detail-label">Min Investment</div>
                <div class="bond-detail-value">$${bond.minimumInvestment}</div>
            </div>
            <div class="bond-detail-item">
                <div class="bond-detail-label">Face Value</div>
                <div class="bond-detail-value">$${(bond.faceValue / 1000).toFixed(0)}K</div>
            </div>
        </div>
        <div class="bond-actions">
            <button class="btn btn-primary" onclick="openInvestmentModal(${bond.id})">Invest</button>
            <button class="btn btn-secondary" onclick="viewBondDetails(${bond.id})">Details</button>
        </div>
    `;
    
    return card;
}

/**
 * Open investment modal
 */
async function openInvestmentModal(bondId) {
    if (!walletManager.isWalletConnected()) {
        alert('Please connect your wallet first');
        return;
    }
    
    currentBondId = bondId;
    
    try {
        const response = await fetch(`${API_BASE_URL}/bonds/${bondId}`);
        const bond = await response.json();
        
        const modal = document.getElementById('investmentModal');
        const detailsDiv = document.getElementById('bondDetails');
        
        const couponRate = (bond.couponRate / 100).toFixed(2);
        const maturityDate = new Date(bond.maturityDate);
        const daysToMaturity = Math.ceil((maturityDate - new Date()) / (1000 * 60 * 60 * 24));
        
        detailsDiv.innerHTML = `
            <h3>${bond.name}</h3>
            <p><strong>Issuer:</strong> ${bond.issuer}</p>
            <p><strong>Coupon Rate:</strong> ${couponRate}%</p>
            <p><strong>Maturity:</strong> ${maturityDate.toLocaleDateString()} (${daysToMaturity} days)</p>
            <p><strong>Minimum Investment:</strong> $${bond.minimumInvestment}</p>
        `;
        
        document.getElementById('investmentAmount').value = bond.minimumInvestment;
        document.getElementById('investmentAmount').min = bond.minimumInvestment;
        
        modal.style.display = 'block';
    } catch (error) {
        console.error('Error loading bond details:', error);
        alert('Failed to load bond details');
    }
}

/**
 * Setup modal close functionality
 */
function setupModal() {
    const modal = document.getElementById('investmentModal');
    const closeBtn = document.querySelector('.close');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }
    
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

/**
 * Setup investment form
 */
function setupInvestmentForm() {
    const form = document.getElementById('investmentForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Check if user is logged in (auth.js exposes isAuthenticated)
        if (typeof isAuthenticated === 'function') {
            if (!isAuthenticated()) {
                alert('Please log in first before investing in bonds');
                return;
            }
        } else if (window.authManager && typeof window.authManager.isAuthenticated === 'function') {
            if (!window.authManager.isAuthenticated()) {
                alert('Please log in first before investing in bonds');
                return;
            }
        } else {
            // Fallback: if auth functions are not available, block investment for safety
            alert('Authentication module not loaded. Please log in to continue.');
            return;
        }
        
        if (!walletManager.isWalletConnected()) {
            alert('Please connect your wallet first');
            return;
        }
        
        const amount = parseFloat(document.getElementById('investmentAmount').value);
        
        if (isNaN(amount) || amount <= 0) {
            alert('Please enter a valid investment amount');
            return;
        }
        
        // Show loading overlay
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        try {
            // Simulate blockchain transaction
            const tx = await walletManager.simulateTransaction(amount, currentBondId);
            
            // Record investment in backend
            const response = await fetch(`${API_BASE_URL}/invest`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getAuthToken()}`
                },
                body: JSON.stringify({
                    bondId: currentBondId,
                    investorAddress: walletManager.getAddress(),
                    amount: amount,
                    timestamp: new Date().toISOString(),
                    transactionHash: tx.hash
                })
            });
            
            if (response.ok) {
                alert('Investment successful! Transaction: ' + tx.hash);
                document.getElementById('investmentModal').style.display = 'none';
                form.reset();
                
                // Refresh portfolio
                if (walletManager.isWalletConnected()) {
                    loadPortfolio();
                }
            } else {
                const error = await response.json();
                alert('Investment failed: ' + (error.detail || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error making investment:', error);
            alert('Failed to process investment: ' + error.message);
        } finally {
            document.getElementById('loadingOverlay').style.display = 'none';
        }
    });
}

/**
 * View bond details and yield information
 */
async function viewBondDetails(bondId) {
    try {
        const [bondResponse, yieldResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/bonds/${bondId}`),
            fetch(`${API_BASE_URL}/yield/${bondId}`)
        ]);
        
        const bond = await bondResponse.json();
        const yieldData = await yieldResponse.json();
        
        const message = `
Bond: ${bond.name}
Issuer: ${bond.issuer}
Coupon Rate: ${(bond.couponRate / 100).toFixed(2)}%
Current Yield: ${yieldData.currentYield.toFixed(2)}%
Annual Interest (per $1000): $${yieldData.annualInterest.toFixed(2)}
Days to Maturity: ${yieldData.daysToMaturity}
        `;
        
        alert(message);
    } catch (error) {
        console.error('Error loading bond details:', error);
        alert('Failed to load bond details');
    }
}

/**
 * Load user portfolio
 */
async function loadPortfolio() {
    if (!walletManager.isWalletConnected()) {
        document.getElementById('portfolioInvestments').innerHTML = 
            '<p class="empty-state">Connect your wallet to view your portfolio</p>';
        return;
    }
    
    try {
        const address = walletManager.getAddress();
        const response = await fetch(`${API_BASE_URL}/portfolio/${address}`);
        const portfolio = await response.json();
        
        // Update stats
        document.getElementById('totalInvested').textContent = 
            '$' + portfolio.totalInvested.toFixed(2);
        document.getElementById('totalValue').textContent = 
            '$' + portfolio.totalValue.toFixed(2);
        document.getElementById('totalYield').textContent = 
            '$' + portfolio.totalYield.toFixed(2);
        
        // Display investments
        const investmentsDiv = document.getElementById('portfolioInvestments');
        
        if (portfolio.investments.length === 0) {
            investmentsDiv.innerHTML = 
                '<p class="empty-state">No investments yet. Start investing in bonds above!</p>';
        } else {
            investmentsDiv.innerHTML = '<h3 style="margin-bottom: 1rem;">Your Investments</h3>';
            
            // Load bond details for each investment
            for (const investment of portfolio.investments) {
                try {
                    const bondResponse = await fetch(`${API_BASE_URL}/bonds/${investment.bondId}`);
                    const bond = await bondResponse.json();
                    
                    const investmentItem = document.createElement('div');
                    investmentItem.className = 'investment-item';
                    investmentItem.innerHTML = `
                        <div class="investment-info">
                            <div class="investment-name">${bond.name}</div>
                            <div class="investment-details">
                                ${bond.issuer} • Invested on ${new Date(investment.timestamp).toLocaleDateString()}
                            </div>
                        </div>
                        <div class="investment-amount">$${investment.amount.toFixed(2)}</div>
                    `;
                    
                    investmentsDiv.appendChild(investmentItem);
                } catch (error) {
                    console.error('Error loading bond for investment:', error);
                }
            }
        }
        
        // Load and display yield chart
        await loadYieldChart(portfolio.investments);
        
    } catch (error) {
        console.error('Error loading portfolio:', error);
        document.getElementById('portfolioInvestments').innerHTML = 
            '<p class="empty-state">Failed to load portfolio. Please check if the backend is running.</p>';
    }
}

/**
 * Load yield chart for portfolio
 */
async function loadYieldChart(investments) {
    if (investments.length === 0) {
        document.getElementById('portfolioChart').style.display = 'none';
        return;
    }
    
    try {
        const chartContainer = document.getElementById('portfolioChart');
        chartContainer.style.display = 'block';
        
        // Get yield data for each bond
        const bondIds = [...new Set(investments.map(inv => inv.bondId))];
        const yieldData = [];
        const labels = [];
        
        for (const bondId of bondIds) {
            try {
                const response = await fetch(`${API_BASE_URL}/yield/${bondId}`);
                const data = await response.json();
                
                const bondResponse = await fetch(`${API_BASE_URL}/bonds/${bondId}`);
                const bond = await bondResponse.json();
                
                labels.push(bond.name);
                yieldData.push(data.currentYield);
            } catch (error) {
                console.error('Error loading yield for bond:', error);
            }
        }
        
        // Create or update chart
        const ctx = document.getElementById('yieldChart').getContext('2d');
        
        if (yieldChart) {
            yieldChart.destroy();
        }
        
        yieldChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Current Yield (%)',
                    data: yieldData,
                    backgroundColor: '#2563eb',
                    borderColor: '#1e40af',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'Yield: ' + context.parsed.y.toFixed(2) + '%';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating yield chart:', error);
    }
}

// Make functions available globally
window.openInvestmentModal = openInvestmentModal;
window.viewBondDetails = viewBondDetails;

// Load portfolio when wallet connects
if (typeof walletManager !== 'undefined') {
    // Check if wallet is already connected on page load
    setTimeout(() => {
        if (walletManager.isWalletConnected()) {
            loadPortfolio();
        }
    }, 500);
}


