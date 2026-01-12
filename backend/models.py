"""
Data models for the Bond Investment Platform
Using Pydantic for FastAPI compatibility and data validation
"""

from pydantic import BaseModel
from typing import List, Optional


class Bond(BaseModel):
    """Bond model"""
    id: int
    name: str
    issuer: str
    faceValue: float
    couponRate: float  # In basis points (e.g., 450 = 4.5%)
    maturityDate: str  # ISO format datetime
    issueDate: str  # ISO format datetime
    description: str
    minimumInvestment: float
    bondTokenAddress: str


class Investment(BaseModel):
    """Investment model"""
    bondId: int
    investorAddress: str
    amount: float
    timestamp: Optional[str] = None
    transactionHash: Optional[str] = None
    user_id: Optional[int] = None
    id: Optional[int] = None


class Portfolio(BaseModel):
    """Portfolio model"""
    address: str
    investments: List[Investment]
    totalInvested: float
    totalValue: float
    totalYield: float


class YieldCalculation(BaseModel):
    """Yield calculation model"""
    bondId: int
    couponRate: float  # Annual rate in percentage
    currentYield: float  # Current yield in percentage
    annualInterest: float  # Annual interest amount
    accruedInterest: float  # Accrued interest since last payment
    daysToMaturity: int
    investorYield: Optional[float] = None  # Yield for specific investor
    investorAccruedInterest: Optional[float] = None


class User(BaseModel):
    """User model"""
    id: int
    email: str
    username: str
    hashed_password: str
    wallet_address: Optional[str] = None  # User's connected wallet address
    created_at: Optional[str] = None


class UserRegister(BaseModel):
    """User registration model"""
    email: str
    username: str
    password: str


class UserLogin(BaseModel):
    """User login model"""
    email: str
    password: str


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str
    user_id: int
    username: str


class AdminUser(BaseModel):
    """Admin user model"""
    id: int
    email: str
    username: str
    is_admin: bool = True
    created_at: Optional[str] = None


class AdminLogin(BaseModel):
    """Admin login model"""
    email: str
    password: str


class BondUpdate(BaseModel):
    """Bond update model for admin"""
    name: Optional[str] = None
    issuer: Optional[str] = None
    faceValue: Optional[float] = None
    couponRate: Optional[float] = None
    maturityDate: Optional[str] = None
    issueDate: Optional[str] = None
    description: Optional[str] = None
    minimumInvestment: Optional[float] = None
    bondTokenAddress: Optional[str] = None


class PaymentAccess(BaseModel):
    """Payment access model"""
    user_id: int
    username: str
    email: str
    wallet_address: Optional[str] = None
    access_level: str  # 'full', 'limited', 'blocked'
    can_invest: bool
    can_withdraw: bool
    can_transfer: bool
    payment_status: str  # 'active', 'suspended', 'blocked'
    created_at: Optional[str] = None


class TransactionHistory(BaseModel):
    """Transaction history model"""
    id: Optional[int] = None
    user_id: int
    type: str  # 'investment', 'withdrawal', 'transfer', 'interest_payment'
    bond_id: Optional[int] = None
    amount: float
    status: str  # 'pending', 'completed', 'failed'
    timestamp: Optional[str] = None
    transaction_hash: Optional[str] = None
    description: Optional[str] = None


class TransactionBill(BaseModel):
    """Transaction bill/receipt model"""
    id: Optional[int] = None
    transaction_id: Optional[int] = None
    user_id: int
    username: str
    email: str
    bond_name: Optional[str] = None
    amount: float
    transaction_type: str
    status: str
    timestamp: Optional[str] = None
    tax_amount: float = 0.0
    fee_amount: float = 0.0
    net_amount: Optional[float] = None

