/**
 * Wallet Connection Module
 * Handles Web3 wallet connection (MetaMask or simulated wallet)
 */

class WalletManager {
    constructor() {
        this.address = null;
        this.isConnected = false;
        this.provider = null;
        this.signer = null;
        
        // Check if MetaMask is available
        this.hasMetaMask = typeof window.ethereum !== 'undefined';
        
        // For demo purposes, create a simulated wallet if MetaMask is not available
        this.simulatedWallet = {
            address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
            balance: 10000 // Simulated balance in USD
        };
        
        // Initialize
        this.initialize();
    }
    
    /**
     * Initialize wallet manager
     */
    initialize() {
        if (this.hasMetaMask) {
            window.ethereum.on('accountsChanged', (accounts) => {
                if (accounts.length > 0) {
                    this.address = accounts[0];
                    this.updateUI();
                    console.log('Account changed:', this.address);
                } else {
                    this.disconnect();
                }
            });
            
            window.ethereum.on('chainChanged', () => {
                console.log('Network changed');
                window.location.reload();
            });
        }
    }
    
    /**
     * Connect to wallet (MetaMask or simulated)
     */
    async connect() {
        try {
            // Require user to be logged in before allowing wallet connection
            if (window.authManager && typeof window.authManager.isAuthenticated === 'function') {
                if (!window.authManager.isAuthenticated()) {
                    alert('Please log in to connect your wallet');
                    if (typeof openModal === 'function') openModal('loginModal');
                    return null;
                }
            }

            if (this.hasMetaMask) {
                // Connect to MetaMask
                console.log('Attempting to connect MetaMask...');
                const accounts = await window.ethereum.request({
                    method: 'eth_requestAccounts'
                });
                
                if (accounts && accounts.length > 0) {
                    this.address = accounts[0];
                    this.isConnected = true;
                    this.provider = window.ethereum;
                    console.log('MetaMask connected successfully:', this.address);
                    return this.address;
                }
            } else {
                // Use simulated wallet for demo (only if logged in)
                console.log('MetaMask not found. Using simulated wallet.');
                this.address = this.simulatedWallet.address;
                this.isConnected = true;
                console.log('Simulated wallet connected:', this.address);
                return this.address;
            }
        } catch (error) {
            console.error('Error connecting wallet:', error);
            // Fallback to simulated wallet
            if (error.code === -32002) {
                alert('MetaMask is already pending a connection request. Please check your MetaMask extension.');
            } else if (error.code === 4001) {
                alert('You rejected the connection request.');
            } else if (error.message && error.message.includes('User denied')) {
                alert('You rejected the connection request.');
            } else {
                alert('Could not connect MetaMask. Using simulated wallet instead.');
                this.address = this.simulatedWallet.address;
                this.isConnected = true;
                console.log('Fallback to simulated wallet');
                return this.address;
            }
            throw error;
        }
    }
    
    /**
     * Disconnect wallet
     */
    disconnect() {
        this.address = null;
        this.isConnected = false;
        this.provider = null;
        this.signer = null;
        console.log('Wallet disconnected');
    }
    
    /**
     * Get current wallet address
     */
    getAddress() {
        return this.address;
    }
    
    /**
     * Check if wallet is connected
     */
    isWalletConnected() {
        return this.isConnected;
    }
    
    /**
     * Format address for display
     */
    formatAddress(address) {
        if (!address) return '';
        return `${address.slice(0, 6)}...${address.slice(-4)}`;
    }
    
    /**
     * Update UI elements
     */
    updateUI() {
        const connectBtn = document.getElementById('connectWalletBtn');
        const walletInfo = document.getElementById('walletInfo');
        const walletAddress = document.getElementById('walletAddress');
        
        if (this.isConnected && this.address) {
            if (connectBtn) connectBtn.style.display = 'none';
            if (walletInfo) walletInfo.style.display = 'flex';
            if (walletAddress) walletAddress.textContent = this.formatAddress(this.address);
        } else {
            if (connectBtn) connectBtn.style.display = 'block';
            if (walletInfo) walletInfo.style.display = 'none';
        }
    }
    
    /**
     * Simulate transaction (for demo purposes)
     */
    async simulateTransaction(amount, bondId) {
        // In a real implementation, this would interact with smart contracts
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    hash: '0x' + Math.random().toString(16).substr(2, 64),
                    success: true
                });
            }, 1500);
        });
    }
}

// Initialize wallet manager
const walletManager = new WalletManager();

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    const connectBtn = document.getElementById('connectWalletBtn');
    const disconnectBtn = document.getElementById('disconnectWalletBtn');
    
    if (connectBtn) {
        connectBtn.addEventListener('click', async () => {
            try {
                connectBtn.disabled = true;
                connectBtn.textContent = 'Connecting...';
                const address = await walletManager.connect();
                walletManager.updateUI();
                
                // Refresh portfolio if on portfolio section
                if (typeof loadPortfolio === 'function') {
                    loadPortfolio();
                }
                console.log('Wallet connected:', address);
            } catch (error) {
                console.error('Wallet connection failed:', error);
            } finally {
                connectBtn.disabled = false;
                connectBtn.textContent = 'Connect Wallet';
            }
        });
    }
    
    if (disconnectBtn) {
        disconnectBtn.addEventListener('click', () => {
            walletManager.disconnect();
            walletManager.updateUI();
            
            // Clear portfolio
            if (typeof loadPortfolio === 'function') {
                loadPortfolio();
            }
            console.log('Wallet disconnected');
        });
    }
});



