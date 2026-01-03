"""
FastAPI Backend for Bond Investment Platform
Manages bond metadata, yield calculations, and user investment records
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os
import msgspec
from dotenv import load_dotenv

from models import Bond, Investment, Portfolio, YieldCalculation
from services import BondService, InvestmentService, YieldCalculator

load_dotenv()

app = FastAPI(title="Bond Investment Platform API", version="1.0.0")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
bond_service = BondService()
investment_service = InvestmentService()
yield_calculator = YieldCalculator()

# Sample bonds data (in production, this would come from a database)
SAMPLE_BONDS = [
    {
        "id": 0,
        "name": "US Treasury 10-Year Bond",
        "issuer": "United States Treasury",
        "faceValue": 1000000,  # $1M total
        "couponRate": 450,  # 4.5% annual
        "maturityDate": (datetime.now() + timedelta(days=3650)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "10-year US Treasury bond with semi-annual interest payments",
        "minimumInvestment": 10,  # $10 minimum
        "bondTokenAddress": "0x0000000000000000000000000000000000000000"  # Placeholder
    },
    {
        "id": 1,
        "name": "UK Gilt 5-Year Bond",
        "issuer": "UK Debt Management Office",
        "faceValue": 500000,  # £500K total
        "couponRate": 400,  # 4.0% annual
        "maturityDate": (datetime.now() + timedelta(days=1825)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "5-year UK government bond with quarterly interest payments",
        "minimumInvestment": 20,  # £20 minimum
        "bondTokenAddress": "0x0000000000000000000000000000000000000001"  # Placeholder
    },
    {
        "id": 2,
        "name": "German Bund 3-Year Bond",
        "issuer": "German Finance Agency",
        "faceValue": 750000,  # €750K total
        "couponRate": 350,  # 3.5% annual
        "maturityDate": (datetime.now() + timedelta(days=1095)).isoformat(),
        "issueDate": datetime.now().isoformat(),
        "description": "3-year German government bond with annual interest payments",
        "minimumInvestment": 15,  # €15 minimum
        "bondTokenAddress": "0x0000000000000000000000000000000000000002"  # Placeholder
    }
]

# Initialize sample bonds
for bond_data in SAMPLE_BONDS:
    bond = msgspec.convert(bond_data, Bond)
    bond_service.add_bond(bond)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Bond Investment Platform API",
        "version": "1.0.0",
        "endpoints": {
            "bonds": "/api/bonds",
            "bond_details": "/api/bonds/{bond_id}",
            "invest": "/api/invest",
            "portfolio": "/api/portfolio/{address}",
            "yield": "/api/yield/{bond_id}"
        }
    }


@app.get("/api/bonds")
async def get_bonds():
    """Get all available bonds"""
    bonds = bond_service.get_all_bonds()
    # Convert msgspec.Struct to dict for JSON serialization
    return [msgspec.to_builtins(bond) for bond in bonds]


@app.get("/api/bonds/{bond_id}")
async def get_bond(bond_id: int):
    """Get details of a specific bond"""
    bond = bond_service.get_bond(bond_id)
    if not bond:
        raise HTTPException(status_code=404, detail="Bond not found")
    return msgspec.to_builtins(bond)


@app.post("/api/invest")
async def record_investment(investment_data: dict):
    """Record an investment transaction"""
    try:
        # Decode investment from JSON using msgspec
        investment = msgspec.convert(investment_data, Investment)
        
        # Validate bond exists
        bond = bond_service.get_bond(investment.bondId)
        if not bond:
            raise HTTPException(status_code=404, detail="Bond not found")
        
        # Validate minimum investment
        if investment.amount < bond.minimumInvestment:
            raise HTTPException(
                status_code=400,
                detail=f"Investment amount must be at least ${bond.minimumInvestment}"
            )
        
        # Record investment
        investment_service.record_investment(investment)
        
        return {
            "success": True,
            "message": "Investment recorded successfully",
            "investment": msgspec.to_builtins(investment)
        }
    except msgspec.ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid investment data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio/{address}")
async def get_portfolio(address: str):
    """Get user portfolio with all investments"""
    investments = investment_service.get_user_investments(address)
    
    # Calculate total value and yields
    total_invested = sum(inv.amount for inv in investments)
    total_value = total_invested  # Simplified - in production, calculate current market value
    
    portfolio = Portfolio(
        address=address,
        investments=investments,
        totalInvested=total_invested,
        totalValue=total_value,
        totalYield=0  # Calculate from individual bond yields
    )
    
    return msgspec.to_builtins(portfolio)


@app.get("/api/yield/{bond_id}")
async def calculate_yield(bond_id: int, address: Optional[str] = None):
    """Calculate current yield for a bond"""
    bond = bond_service.get_bond(bond_id)
    if not bond:
        raise HTTPException(status_code=404, detail="Bond not found")
    
    # Calculate yield
    yield_data = yield_calculator.calculate_yield(bond, address)
    
    return msgspec.to_builtins(yield_data)


@app.get("/api/bonds/{bond_id}/stats")
async def get_bond_stats(bond_id: int):
    """Get statistics for a bond"""
    bond = bond_service.get_bond(bond_id)
    if not bond:
        raise HTTPException(status_code=404, detail="Bond not found")
    
    # Get all investments for this bond
    all_investments = investment_service.get_all_investments()
    bond_investments = [inv for inv in all_investments if inv.bondId == bond_id]
    
    total_invested = sum(inv.amount for inv in bond_investments)
    investor_count = len(set(inv.investorAddress for inv in bond_investments))
    
    # Calculate days to maturity
    maturity_date = datetime.fromisoformat(bond.maturityDate.replace('Z', '+00:00'))
    days_to_maturity = (maturity_date - datetime.now()).days
    
    return {
        "bondId": bond_id,
        "totalInvested": total_invested,
        "investorCount": investor_count,
        "daysToMaturity": days_to_maturity,
        "couponRate": bond.couponRate / 100,  # Convert to percentage
        "faceValue": bond.faceValue,
        "utilization": (total_invested / bond.faceValue * 100) if bond.faceValue > 0 else 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

