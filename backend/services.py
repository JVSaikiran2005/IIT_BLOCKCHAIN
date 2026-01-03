"""
Business logic services for the Bond Investment Platform
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from models import Bond, Investment, YieldCalculation


class BondService:
    """Service for managing bonds"""
    
    def __init__(self):
        self.bonds: Dict[int, Bond] = {}
    
    def add_bond(self, bond: Bond):
        """Add a bond to the service"""
        self.bonds[bond.id] = bond
    
    def get_bond(self, bond_id: int) -> Optional[Bond]:
        """Get a bond by ID"""
        return self.bonds.get(bond_id)
    
    def get_all_bonds(self) -> List[Bond]:
        """Get all bonds"""
        return list(self.bonds.values())


class InvestmentService:
    """Service for managing investments"""
    
    def __init__(self):
        self.investments: List[Investment] = []
    
    def record_investment(self, investment: Investment):
        """Record an investment"""
        if investment.timestamp is None:
            investment.timestamp = datetime.now().isoformat()
        self.investments.append(investment)
    
    def get_user_investments(self, address: str) -> List[Investment]:
        """Get all investments for a user address"""
        return [inv for inv in self.investments if inv.investorAddress.lower() == address.lower()]
    
    def get_bond_investments(self, bond_id: int) -> List[Investment]:
        """Get all investments for a bond"""
        return [inv for inv in self.investments if inv.bondId == bond_id]
    
    def get_all_investments(self) -> List[Investment]:
        """Get all investments"""
        return self.investments


class YieldCalculator:
    """Service for calculating bond yields"""
    
    def calculate_yield(self, bond: Bond, investor_address: Optional[str] = None) -> YieldCalculation:
        """Calculate yield for a bond"""
        # Parse dates
        maturity_date = datetime.fromisoformat(bond.maturityDate.replace('Z', '+00:00'))
        issue_date = datetime.fromisoformat(bond.issueDate.replace('Z', '+00:00'))
        
        # Calculate days to maturity
        days_to_maturity = (maturity_date - datetime.now()).days
        
        # Convert coupon rate from basis points to percentage
        coupon_rate_pct = bond.couponRate / 100
        
        # Calculate annual interest (assuming $1000 investment for example)
        example_investment = 1000.0
        annual_interest = (example_investment * bond.couponRate) / 10000
        
        # Calculate accrued interest (simplified - assumes daily accrual)
        days_since_issue = (datetime.now() - issue_date).days
        accrued_interest = (annual_interest * days_since_issue) / 365
        
        # Current yield equals coupon rate for bonds at par
        current_yield = coupon_rate_pct
        
        result = YieldCalculation(
            bondId=bond.id,
            couponRate=coupon_rate_pct,
            currentYield=current_yield,
            annualInterest=annual_interest,
            accruedInterest=accrued_interest,
            daysToMaturity=days_to_maturity
        )
        
        # If investor address provided, calculate investor-specific yield
        if investor_address:
            # In production, this would query the blockchain for actual token balance
            # For now, we'll use a simplified calculation
            investor_yield = coupon_rate_pct
            investor_accrued = accrued_interest
            
            result.investorYield = investor_yield
            result.investorAccruedInterest = investor_accrued
        
        return result

