# Quick Start Guide

Get the Bond Investment Platform running in 5 minutes!

## Step 1: Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies (for smart contracts - optional)
cd contracts
npm install
cd ..
```

## Step 2: Start the Backend

```bash
# Windows
start_backend.bat

# Linux/Mac
chmod +x start_backend.sh
./start_backend.sh

# Or manually:
cd backend
python app.py
```

The backend will start at `http://localhost:8000`

## Step 3: Start the Frontend

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Start HTTP server
python -m http.server 8080
```

Or simply open `frontend/index.html` in your browser (some features may not work without a server due to CORS).

## Step 4: Use the Platform

1. Open `http://localhost:8080` in your browser
2. Click "Connect Wallet" (uses simulated wallet if MetaMask not installed)
3. Browse available bonds
4. Click "Invest" on any bond
5. Enter investment amount and confirm
6. View your portfolio in "My Portfolio" section

## Testing the API

You can test the API endpoints directly:

```bash
# Get all bonds
curl http://localhost:8000/api/bonds

# Get bond details
curl http://localhost:8000/api/bonds/0

# Get portfolio (replace with your address)
curl http://localhost:8000/api/portfolio/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb

# Calculate yield
curl http://localhost:8000/api/yield/0
```

## Troubleshooting

### Backend won't start
- Make sure Python 3.8+ is installed
- Check if port 8000 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend can't connect to backend
- Ensure backend is running on `http://localhost:8000`
- Check browser console for CORS errors
- Make sure you're accessing frontend via HTTP server, not file://

### Wallet connection issues
- If MetaMask is installed, make sure it's unlocked
- The platform will use a simulated wallet if MetaMask is not available
- Check browser console for Web3 connection errors

## Next Steps

- Deploy smart contracts to a local blockchain (see README.md)
- Connect to a testnet for real blockchain interaction
- Customize bonds and add more features

For detailed documentation, see [README.md](README.md)

