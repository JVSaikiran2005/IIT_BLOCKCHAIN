"""
Business logic services for the Bond Investment Platform
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from models import Bond, Investment, YieldCalculation, User
from passlib.context import CryptContext


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


class UserService:
    """Service for managing users and authentication"""
    
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.users_by_email: Dict[str, User] = {}
        self.users_by_username: Dict[str, User] = {}
        self.next_user_id = 1
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, email: str, username: str, password: str) -> User:
        """Create a new user"""
        # Check if email already exists
        if email.lower() in self.users_by_email:
            raise ValueError("Email already registered")
        
        # Check if username already exists
        if username.lower() in self.users_by_username:
            raise ValueError("Username already taken")
        
        # Create user
        user_id = self.next_user_id
        self.next_user_id += 1
        
        hashed_password = self.hash_password(password)
        user = User(
            id=user_id,
            email=email.lower(),
            username=username,
            hashed_password=hashed_password,
            created_at=datetime.now().isoformat()
        )
        
        self.users[user_id] = user
        self.users_by_email[email.lower()] = user
        self.users_by_username[username.lower()] = user
        
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.users_by_email.get(email.lower())
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        return user


