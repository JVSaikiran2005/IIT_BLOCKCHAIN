"""
Configuration for the Bond Investment Platform
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Blockchain configuration
BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://localhost:8545")
BOND_PLATFORM_CONTRACT_ADDRESS = os.getenv("BOND_PLATFORM_CONTRACT_ADDRESS", "")
STABLECOIN_CONTRACT_ADDRESS = os.getenv("STABLECOIN_CONTRACT_ADDRESS", "")

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Database configuration (for future use)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bonds.db")


