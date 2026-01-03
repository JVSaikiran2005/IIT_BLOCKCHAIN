# Blockchain-Based Government Bond Investment Platform

A decentralized platform that tokenizes government bonds into fractional units, making them accessible to retail investors, students, and young professionals. The platform focuses on financial inclusion by reducing high minimum investment requirements, simplifying onboarding, and improving transparency through blockchain technology.

## 🌟 Features

- **Fractional Ownership**: Invest in government bonds with minimal amounts (as low as $10) using stablecoins
- **Transparency**: All transactions and ownership records are stored on-chain
- **Automated Yields**: Smart contracts handle interest calculations and periodic payouts automatically
- **User-Friendly Interface**: Clean, beginner-friendly frontend built with HTML, CSS, and JavaScript
- **Global Accessibility**: No high minimum investment requirements - invest what you can afford
- **Real-Time Visualization**: View bond yields, interest rates, and maturity timelines with interactive charts

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│              HTML/CSS/JavaScript + Web3.js                   │
│  - Wallet Connection (MetaMask/Simulated)                      │
│  - Bond Browsing & Investment Interface                      │
│  - Portfolio Management & Visualization                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌─────────▼──────────┐
│  Backend API   │            │  Blockchain Layer  │
│   (FastAPI)    │            │  (Smart Contracts)│
│                │            │                    │
│ - Bond Metadata│            │ - BondToken.sol    │
│ - Yield Calc   │◄──────────►│ - BondPlatform.sol│
│ - Investment   │            │ - MockStablecoin   │
│   Records      │            │ - Yield Distribution│
└────────────────┘            └────────────────────┘
        │
        │
┌───────▼────────┐
│  Off-Chain     │
│  Bond Custody  │
│  (Simulated)   │
└────────────────┘
```

## 📁 Project Structure

```
iit/
├── contracts/                  # Solidity smart contracts
│   ├── BondToken.sol          # ERC-20 compatible bond token
│   ├── BondPlatform.sol       # Factory contract for creating bonds
│   ├── MockStablecoin.sol     # Mock stablecoin for testing
│   ├── scripts/
│   │   └── deploy.js          # Deployment script
│   ├── hardhat.config.js      # Hardhat configuration
│   └── package.json           # Node.js dependencies
├── backend/                    # Python FastAPI backend
│   ├── app.py                 # Main application
│   ├── models.py              # msgspec data models
│   ├── services.py            # Business logic
│   ├── config.py              # Configuration
│   └── blockchain_utils.py    # Blockchain utilities (eth-abi, requests)
├── frontend/                   # HTML/CSS/JavaScript frontend
│   ├── index.html             # Main page
│   ├── styles.css             # Styling
│   ├── app.js                 # Main application logic
│   └── wallet.js              # Wallet connection logic
├── requirements.txt           # Python dependencies
├── package.json               # Frontend dependencies
└── README.md                  # This file
```

## 🚀 Setup Instructions

### Prerequisites

- **Python 3.13.7** - For backend API (tested with Python 3.13.7)
- **Node.js 14+** - For smart contract compilation and frontend dependencies
- **MetaMask** (optional) - For Web3 wallet connection, or use simulated wallet
- **Hardhat** (optional) - For local blockchain development

### 1. Clone and Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for contracts)
cd contracts
npm install

# Install frontend dependencies (optional, for local development)
cd ../frontend
# Dependencies are loaded via CDN, but you can install locally if needed
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Run the FastAPI server
python app.py
```

The API will be available at `http://localhost:8000`

You can also use uvicorn directly:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 3. Smart Contracts Setup (Optional - for full blockchain integration)

#### Local Development with Hardhat

```bash
cd contracts

# Start local Hardhat node
npx hardhat node

# In another terminal, deploy contracts
npx hardhat run scripts/deploy.js --network localhost
```

#### Update Environment Variables

Create a `.env` file in the `backend` directory:

```env
BLOCKCHAIN_RPC_URL=http://localhost:8545
BOND_PLATFORM_CONTRACT_ADDRESS=0x...
STABLECOIN_CONTRACT_ADDRESS=0x...
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Start a local HTTP server
python -m http.server 8080
```

Or use the npm script:
```bash
npm start
```

Access the application at `http://localhost:8080`

**Note**: Make sure the backend is running before using the frontend, as it depends on the API endpoints.

## 📡 API Endpoints

### Bonds

- `GET /api/bonds` - List all available bonds
- `GET /api/bonds/{bond_id}` - Get bond details
- `GET /api/bonds/{bond_id}/stats` - Get bond statistics

### Investments

- `POST /api/invest` - Record an investment
  ```json
  {
    "bondId": 0,
    "investorAddress": "0x...",
    "amount": 100.0,
    "timestamp": "2024-01-01T12:00:00",
    "transactionHash": "0x..."
  }
  ```

### Portfolio

- `GET /api/portfolio/{address}` - Get user portfolio
- `GET /api/yield/{bond_id}` - Calculate current yield for a bond
  - Query parameter: `address` (optional) - Calculate yield for specific investor

## 🔐 Smart Contract Functions

### BondToken Contract

- `invest(uint256 stablecoinAmount)` - Invest in the bond by purchasing tokens
- `claimInterest()` - Claim accrued interest payments
- `redeem()` - Redeem principal at maturity
- `calculateAccruedInterest(address investor)` - View accrued interest for an investor
- `getBondInfo()` - Get bond information

### BondPlatform Contract

- `createBond(...)` - Create a new bond token (owner only)
- `getBondCount()` - Get total number of bonds
- `getAllBonds()` - Get all bond token addresses
- `getBondToken(uint256 bondId)` - Get bond token address by ID

## 💡 Usage Guide

### 1. Connect Wallet

- Click "Connect Wallet" button
- If MetaMask is installed, it will prompt for connection
- If not, a simulated wallet will be used for demo purposes

### 2. Browse Bonds

- View available government bonds from different countries
- See coupon rates, maturity dates, and minimum investments
- Click "Details" to view more information and yield calculations

### 3. Invest

- Click "Invest" on any bond card
- Enter your investment amount (minimum shown)
- Confirm the transaction
- Your investment will be recorded and tokens minted

### 4. View Portfolio

- Navigate to "My Portfolio" section
- See total invested, current value, and yields
- View individual investments
- Check yield charts for visual representation

### 5. Claim Interest & Redeem

- Interest accrues automatically based on coupon rate
- Use smart contract functions to claim interest payments
- Redeem principal when bonds reach maturity

## 🔒 Security Considerations

- **Smart Contracts**: Contracts use OpenZeppelin libraries for security
- **Reentrancy Protection**: All state-changing functions use ReentrancyGuard
- **Access Control**: Owner-only functions for administrative tasks
- **Input Validation**: All user inputs are validated on both frontend and backend

## 🧪 Testing

### Backend Testing

```bash
cd backend
python -m pytest  # If tests are added
```

### Smart Contract Testing

```bash
cd contracts
npx hardhat test
```

## 🌐 Production Deployment

For production deployment:

1. **Deploy Smart Contracts** to a production network (Ethereum, Polygon, etc.)
2. **Update Contract Addresses** in backend `.env` file
3. **Configure CORS** in `backend/app.py` to allow only your frontend domain
4. **Use Real Stablecoins** (USDC, USDT, DAI) instead of mock stablecoin
5. **Set up Database** for persistent storage (replace in-memory storage)
6. **Add Authentication** for API endpoints if needed
7. **Deploy Frontend** to a static hosting service (Vercel, Netlify, etc.)

## 📊 Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Chart.js
- **Backend**: Python 3.13.7, FastAPI, msgspec (replaces Pydantic)
- **Blockchain**: Solidity 0.8.19, OpenZeppelin Contracts
- **Blockchain Utils**: eth-abi, requests (replaces web3.py)
- **Development**: Hardhat, Web3.js (frontend), MetaMask

## 🤝 Contributing

This is a demonstration project. For production use, consider:

- Adding comprehensive test coverage
- Implementing proper database storage
- Adding user authentication and authorization
- Implementing rate limiting and API security
- Adding more sophisticated yield calculations
- Integrating with real bond market data
- Adding multi-chain support

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- OpenZeppelin for secure smart contract libraries
- FastAPI for the excellent Python web framework
- Chart.js for data visualization

## 📧 Support

For questions or issues, please open an issue on the repository.

---

**Built for financial inclusion** - Making safe, low-risk investments accessible to everyone through blockchain technology.
