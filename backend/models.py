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

