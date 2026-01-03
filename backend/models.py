"""
Data models for the Bond Investment Platform
Using msgspec for data validation (Python 3.13.7 compatible)
"""

import msgspec
from typing import List, Optional


class Bond(msgspec.Struct):
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


class Investment(msgspec.Struct):
    """Investment model"""
    bondId: int
    investorAddress: str
    amount: float
    timestamp: Optional[str] = None
    transactionHash: Optional[str] = None


class Portfolio(msgspec.Struct):
    """Portfolio model"""
    address: str
    investments: List[Investment]
    totalInvested: float
    totalValue: float
    totalYield: float


class YieldCalculation(msgspec.Struct):
    """Yield calculation model"""
    bondId: int
    couponRate: float  # Annual rate in percentage
    currentYield: float  # Current yield in percentage
    annualInterest: float  # Annual interest amount
    accruedInterest: float  # Accrued interest since last payment
    daysToMaturity: int
    investorYield: Optional[float] = None  # Yield for specific investor
    investorAccruedInterest: Optional[float] = None

