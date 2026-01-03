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
    }
    
    /**
     * Connect to wallet (MetaMask or simulated)
     */
    async connect() {
        try {
            if (this.hasMetaMask) {
                // Connect to MetaMask
                const accounts = await window.ethereum.request({
                    method: 'eth_requestAccounts'
                });
                
                if (accounts.length > 0) {
                    this.address = accounts[0];
                    this.isConnected = true;
                    this.provider = window.ethereum;
                    
                    // Listen for account changes
                    window.ethereum.on('accountsChanged', (accounts) => {
                        if (accounts.length > 0) {
                            this.address = accounts[0];
                            this.updateUI();
                        } else {
                            this.disconnect();
                        }
                    });
                    
                    return this.address;
                }
            } else {
                // Use simulated wallet for demo
                this.address = this.simulatedWallet.address;
                this.isConnected = true;
                return this.address;
            }
        } catch (error) {
            console.error('Error connecting wallet:', error);
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
        
        if (this.isConnected) {
            connectBtn.style.display = 'none';
            walletInfo.style.display = 'flex';
            walletAddress.textContent = this.formatAddress(this.address);
        } else {
            connectBtn.style.display = 'block';
            walletInfo.style.display = 'none';
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
                await walletManager.connect();
                walletManager.updateUI();
                
                // Refresh portfolio if on portfolio section
                if (typeof loadPortfolio === 'function') {
                    loadPortfolio();
                }
            } catch (error) {
                alert('Failed to connect wallet: ' + error.message);
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
        });
    }
});

