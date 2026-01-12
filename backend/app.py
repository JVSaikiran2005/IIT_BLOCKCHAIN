"""
FastAPI Backend for Bond Investment Platform
Manages bond metadata, yield calculations, and user investment records
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

from models import Bond, Investment, Portfolio, YieldCalculation, UserRegister, UserLogin, Token, User, BondUpdate
from services import BondService, InvestmentService, YieldCalculator, UserService
from auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, set_user_service
from admin_auth import create_admin_access_token, get_current_admin, authenticate_admin, ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES
from database import init_db_instance

load_dotenv()

app = FastAPI(title="Bond Investment Platform API", version="1.0.0")

# Initialize database
init_db_instance()

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
user_service = UserService()

# Initialize auth with user service
set_user_service(user_service)

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
    bond = Bond(**bond_data)
    bond_service.add_bond(bond)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Bond Investment Platform API",
        "version": "1.0.0",
        "endpoints": {
            "register": "/api/auth/register",
            "login": "/api/auth/login",
            "me": "/api/auth/me",
            "bonds": "/api/bonds",
            "bond_details": "/api/bonds/{bond_id}",
            "invest": "/api/invest",
            "portfolio": "/api/portfolio/{address}",
            "yield": "/api/yield/{bond_id}"
        }
    }


@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    """Register a new user"""
    print(f"DEBUG: Register endpoint called with email={user_data.email}")
    try:
        print(f"DEBUG: About to call create_user")
        user = user_service.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password
        )
        print(f"DEBUG: create_user returned: {user}")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id, "username": user.username},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            username=user.username
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@app.post("/api/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user"""
    user = user_service.authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username
    )


@app.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "created_at": current_user.created_at
    }


@app.get("/api/bonds")
async def get_bonds():
    """Get all available bonds"""
    bonds = bond_service.get_all_bonds()
    # Convert Pydantic models to dict for JSON serialization
    return [bond.model_dump() for bond in bonds]


@app.get("/api/bonds/{bond_id}")
async def get_bond(bond_id: int):
    """Get details of a specific bond"""
    bond = bond_service.get_bond(bond_id)
    if not bond:
        raise HTTPException(status_code=404, detail="Bond not found")
    return bond.model_dump()


@app.post("/api/invest")
async def record_investment(investment_data: Investment, current_user: User = Depends(get_current_user)):
    """Record an investment transaction and persist it to the database."""
    try:
        investment = investment_data

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

        # Persist investment with associated user id
        record = investment_service.record_investment(investment, user_id=current_user.id)

        return {
            "success": True,
            "message": "Investment recorded successfully",
            "investment": record
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio")
async def get_portfolio(current_user: User = Depends(get_current_user)):
    """Get user portfolio with all investments (PRIVATE - requires authentication)"""
    # Get investments for the current user by user ID
    investments = investment_service.get_user_investments_by_id(current_user.id)
    
    # Calculate total value and yields
    total_invested = sum(inv.amount for inv in investments)
    total_value = total_invested  # Simplified - in production, calculate current market value
    
    portfolio = Portfolio(
        address=current_user.wallet_address or "wallet_not_connected",
        investments=investments,
        totalInvested=total_invested,
        totalValue=total_value,
        totalYield=0  # Calculate from individual bond yields
    )
    
    return portfolio.model_dump()


@app.get("/api/yield/{bond_id}")
async def calculate_yield(bond_id: int, address: Optional[str] = None):
    """Calculate current yield for a bond"""
    bond = bond_service.get_bond(bond_id)
    if not bond:
        raise HTTPException(status_code=404, detail="Bond not found")
    
    # Calculate yield
    yield_data = yield_calculator.calculate_yield(bond, address)
    
    return yield_data.model_dump()


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


@app.post("/api/bonds")
async def create_bond(bond_data: Bond, current_user: User = Depends(get_current_user)):
    """Create a new bond (admin only)"""
    try:
        # In production, add role-based access control here
        # For now, allow any authenticated user
        bond_service.add_bond(bond_data)
        return {
            "success": True,
            "message": "Bond created successfully",
            "bond": bond_data.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/investments/user/{user_id}")
async def get_user_investments_by_id(user_id: int, current_user: User = Depends(get_current_user)):
    """Get all investments for a specific user"""
    try:
        investments = investment_service.db.get_user_investments(user_id) if investment_service.db else []
        return {
            "userId": user_id,
            "investments": investments,
            "totalInvested": sum(inv['amount'] for inv in investments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/investments/stats")
async def get_investment_statistics():
    """Get overall investment platform statistics"""
    try:
        all_investments = investment_service.get_all_investments()
        all_bonds = bond_service.get_all_bonds()
        
        total_invested = sum(inv.amount for inv in all_investments)
        total_investors = len(set(inv.investorAddress for inv in all_investments))
        
        # Calculate bond-wise statistics
        bond_stats = {}
        for bond in all_bonds:
            bond_invs = [inv for inv in all_investments if inv.bondId == bond.id]
            bond_stats[bond.id] = {
                "name": bond.name,
                "totalInvested": sum(inv.amount for inv in bond_invs),
                "investorCount": len(set(inv.investorAddress for inv in bond_invs)),
                "investmentCount": len(bond_invs)
            }
        
        return {
            "totalInvested": total_invested,
            "totalInvestors": total_investors,
            "totalInvestments": len(all_investments),
            "totalBonds": len(all_bonds),
            "bondStats": bond_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/investments/bond/{bond_id}")
async def get_bond_investments(bond_id: int):
    """Get all investments for a specific bond"""
    try:
        bond = bond_service.get_bond(bond_id)
        if not bond:
            raise HTTPException(status_code=404, detail="Bond not found")
        
        investments = investment_service.get_bond_investments(bond_id)
        
        return {
            "bondId": bond_id,
            "bondName": bond.name,
            "investments": [inv.model_dump() for inv in investments],
            "totalInvested": sum(inv.amount for inv in investments),
            "investorCount": len(set(inv.investorAddress for inv in investments))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =======================
# ADMIN ENDPOINTS
# =======================

@app.post("/api/admin/login")
async def admin_login(admin_data: UserLogin):
    """Admin login endpoint"""
    admin = authenticate_admin(admin_data.email, admin_data.password)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_admin_access_token(
        data={"sub": admin["email"], "user_id": admin["user_id"], "username": admin["username"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": admin["user_id"],
        "username": admin["username"],
        "email": admin["email"]
    }


@app.get("/api/admin/users")
async def get_all_users_with_investments(admin: dict = Depends(get_current_admin)):
    """Get all users and their investments (admin only)"""
    try:
        # Get all users
        all_investments = investment_service.get_all_investments()
        all_bonds = bond_service.get_all_bonds()
        
        # Group investments by user_id
        users_dict = {}
        
        if investment_service.db:
            # Get users from database
            users_data = investment_service.db.get_all_users()
            for user_row in users_data:
                user_id = user_row['id']
                users_dict[user_id] = {
                    "id": user_id,
                    "email": user_row['email'],
                    "username": user_row['username'],
                    "created_at": user_row['created_at'],
                    "investments": []
                }
        
        # Add investments to users
        for inv in all_investments:
            user_id = inv.user_id if hasattr(inv, 'user_id') else None
            if user_id and user_id in users_dict:
                users_dict[user_id]["investments"].append({
                    "id": inv.id if hasattr(inv, 'id') else None,
                    "bond_id": inv.bondId,
                    "amount": inv.amount,
                    "timestamp": inv.timestamp,
                    "investor_address": inv.investorAddress
                })
        
        # Calculate statistics
        total_invested = sum(inv.amount for inv in all_investments)
        total_investments = len(all_investments)
        total_users = len(users_dict)
        
        return {
            "users": list(users_dict.values()),
            "total_users": total_users,
            "total_investments": total_investments,
            "total_invested": total_invested,
            "total_bonds": len(all_bonds)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/user/{user_id}")
async def get_user_investments_admin(user_id: int, admin: dict = Depends(get_current_admin)):
    """Get detailed investments for a specific user (admin only)"""
    try:
        if investment_service.db:
            user_data = investment_service.db.get_user_by_id(user_id)
            if not user_data:
                raise HTTPException(status_code=404, detail="User not found")
            
            investments = investment_service.get_user_investments_by_id(user_id)
            
            return {
                "user": {
                    "id": user_data['id'],
                    "email": user_data['email'],
                    "username": user_data['username'],
                    "created_at": user_data['created_at']
                },
                "investments": [
                    {
                        "bond_id": inv.bondId,
                        "amount": inv.amount,
                        "timestamp": inv.timestamp,
                        "investor_address": inv.investorAddress
                    }
                    for inv in investments
                ],
                "total_invested": sum(inv.amount for inv in investments),
                "investment_count": len(investments)
            }
        else:
            raise HTTPException(status_code=500, detail="Database not available")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =======================
# ADMIN BOND MANAGEMENT
# =======================

@app.post("/api/admin/bonds")
async def admin_create_bond(bond_data: Bond, admin: dict = Depends(get_current_admin)):
    """Create a new government bond (admin only)"""
    try:
        bond_service.add_bond(bond_data)
        return {
            "success": True,
            "message": "Bond created successfully",
            "bond": bond_data.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/bonds")
async def admin_get_all_bonds(admin: dict = Depends(get_current_admin)):
    """Get all bonds (admin view)"""
    try:
        bonds = bond_service.get_all_bonds()
        return {
            "total_bonds": len(bonds),
            "bonds": [bond.model_dump() for bond in bonds]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/bonds/{bond_id}")
async def admin_get_bond(bond_id: int, admin: dict = Depends(get_current_admin)):
    """Get specific bond details (admin view)"""
    try:
        bond = bond_service.get_bond(bond_id)
        if not bond:
            raise HTTPException(status_code=404, detail="Bond not found")
        
        # Get investment stats for this bond
        all_investments = investment_service.get_all_investments()
        bond_investments = [inv for inv in all_investments if inv.bondId == bond_id]
        
        return {
            "bond": bond.model_dump(),
            "total_invested": sum(inv.amount for inv in bond_investments),
            "investor_count": len(set(inv.investorAddress for inv in bond_investments)),
            "investment_count": len(bond_investments)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/admin/bonds/{bond_id}")
async def admin_update_bond(bond_id: int, bond_update: BondUpdate, admin: dict = Depends(get_current_admin)):
    """Update bond details (admin only)"""
    try:
        bond = bond_service.get_bond(bond_id)
        if not bond:
            raise HTTPException(status_code=404, detail="Bond not found")
        
        # Update bond fields
        update_data = bond_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(bond, key, value)
        
        bond_service.bonds[bond_id] = bond
        
        return {
            "success": True,
            "message": f"Bond {bond_id} updated successfully",
            "bond": bond.model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/admin/bonds/{bond_id}")
async def admin_delete_bond(bond_id: int, admin: dict = Depends(get_current_admin)):
    """Delete a bond (admin only)"""
    try:
        bond = bond_service.get_bond(bond_id)
        if not bond:
            raise HTTPException(status_code=404, detail="Bond not found")
        
        del bond_service.bonds[bond_id]
        
        return {
            "success": True,
            "message": f"Bond {bond_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =======================
# ADMIN USER MANAGEMENT & PAYMENT ACCESS
# =======================

@app.get("/api/admin/users/full")
async def admin_get_all_users_full(admin: dict = Depends(get_current_admin)):
    """Get all users with full details including credentials (admin only)"""
    try:
        users_data = investment_service.db.get_all_users() if investment_service.db else []
        
        result = []
        for user_row in users_data:
            user_id = user_row['id']
            
            # Get payment access
            payment_access = investment_service.db.get_payment_access(user_id) if investment_service.db else None
            
            # Get transactions
            transactions = investment_service.db.get_user_transactions(user_id) if investment_service.db else []
            
            # Get bills
            bills = investment_service.db.get_user_bills(user_id) if investment_service.db else []
            
            # Get investments
            investments = investment_service.get_user_investments_by_id(user_id)
            
            result.append({
                "id": user_id,
                "email": user_row['email'],
                "username": user_row['username'],
                "hashed_password": user_row['hashed_password'],
                "created_at": user_row['created_at'],
                "payment_access": payment_access or {"status": "not_configured"},
                "transaction_count": len(transactions),
                "bill_count": len(bills),
                "investment_count": len(investments),
                "total_invested": sum(inv.amount for inv in investments),
                "login_credentials": {
                    "email": user_row['email'],
                    "username": user_row['username'],
                    "password_hash": user_row['hashed_password']
                }
            })
        
        return {
            "total_users": len(result),
            "users": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/payment-access")
async def admin_get_all_payment_access(admin: dict = Depends(get_current_admin)):
    """Get payment access for all users (admin only)"""
    try:
        payment_access_list = investment_service.db.get_all_payment_access() if investment_service.db else []
        
        return {
            "total_records": len(payment_access_list),
            "payment_access": payment_access_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/admin/payment-access/{user_id}")
async def admin_update_payment_access(user_id: int, access_update: dict, admin: dict = Depends(get_current_admin)):
    """Update user's payment access (admin only)"""
    try:
        if not investment_service.db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Verify user exists
        user = investment_service.db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if payment access exists, create if not
        payment_access = investment_service.db.get_payment_access(user_id)
        if not payment_access:
            investment_service.db.create_payment_access(user_id)
        
        # Update payment access
        updated = investment_service.db.update_payment_access(user_id, **access_update)
        
        return {
            "success": True,
            "message": f"Payment access for user {user_id} updated successfully",
            "payment_access": updated
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =======================
# ADMIN TRANSACTION MANAGEMENT
# =======================

@app.get("/api/admin/transactions")
async def admin_get_all_transactions(admin: dict = Depends(get_current_admin)):
    """Get all transactions (admin only)"""
    try:
        transactions = investment_service.db.get_all_transactions() if investment_service.db else []
        
        # Group by status
        by_status = {}
        for trans in transactions:
            status = trans['status']
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(trans)
        
        return {
            "total_transactions": len(transactions),
            "by_status": by_status,
            "transactions": transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/transactions/{user_id}")
async def admin_get_user_transactions(user_id: int, admin: dict = Depends(get_current_admin)):
    """Get transactions for specific user (admin only)"""
    try:
        if not investment_service.db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        user = investment_service.db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        transactions = investment_service.db.get_user_transactions(user_id)
        
        return {
            "user_id": user_id,
            "username": user['username'],
            "email": user['email'],
            "total_transactions": len(transactions),
            "transactions": transactions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =======================
# ADMIN BILLS MANAGEMENT
# =======================

@app.get("/api/admin/bills")
async def admin_get_all_bills(admin: dict = Depends(get_current_admin)):
    """Get all transaction bills (admin only)"""
    try:
        bills = investment_service.db.get_all_bills() if investment_service.db else []
        
        # Calculate totals
        total_amount = sum(bill['amount'] for bill in bills)
        total_tax = sum(bill['tax_amount'] for bill in bills)
        total_fee = sum(bill['fee_amount'] for bill in bills)
        total_net = sum(bill['net_amount'] for bill in bills)
        
        return {
            "total_bills": len(bills),
            "summary": {
                "total_amount": total_amount,
                "total_tax": total_tax,
                "total_fee": total_fee,
                "total_net": total_net
            },
            "bills": bills
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/bills/{user_id}")
async def admin_get_user_bills(user_id: int, admin: dict = Depends(get_current_admin)):
    """Get bills for specific user (admin only)"""
    try:
        if not investment_service.db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        user = investment_service.db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        bills = investment_service.db.get_user_bills(user_id)
        
        total_amount = sum(bill['amount'] for bill in bills)
        total_tax = sum(bill['tax_amount'] for bill in bills)
        total_fee = sum(bill['fee_amount'] for bill in bills)
        total_net = sum(bill['net_amount'] for bill in bills)
        
        return {
            "user_id": user_id,
            "username": user['username'],
            "email": user['email'],
            "total_bills": len(bills),
            "summary": {
                "total_amount": total_amount,
                "total_tax": total_tax,
                "total_fee": total_fee,
                "total_net": total_net
            },
            "bills": bills
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

