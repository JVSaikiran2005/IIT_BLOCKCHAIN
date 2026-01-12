"""
Business logic services for the Bond Investment Platform
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from models import Bond, Investment, YieldCalculation, User
from passlib.context import CryptContext
from database import get_db


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
        # Use persistent database for investments when available
        self.db = get_db()
        self.investments: List[Investment] = []
    
    def record_investment(self, investment: Investment, user_id: Optional[int] = None) -> dict:
        """Record an investment. Persist to DB when possible.

        If `user_id` is provided, the investment will be stored in the SQLite
        database and the created DB record will be returned. Otherwise falls
        back to in-memory storage for test/demo purposes.
        """
        if investment.timestamp is None:
            investment.timestamp = datetime.now().isoformat()

        if user_id is not None and self.db:
            # Persist to DB
            record = self.db.record_investment(
                user_id=user_id,
                bond_id=investment.bondId,
                investor_address=investment.investorAddress,
                amount=investment.amount,
                timestamp=investment.timestamp,
                transaction_hash=investment.transactionHash
            )
            return record

        # Fallback: in-memory
        self.investments.append(investment)
        return investment.model_dump()
    
    def get_user_investments(self, address: str) -> List[Investment]:
        """Get all investments for a user address (by wallet address)."""
        results: List[Investment] = []
        if self.db:
            rows = self.db.get_investments_by_address(address)
            for r in rows:
                inv = Investment(
                    bondId=r['bond_id'],
                    investorAddress=r['investor_address'],
                    amount=r['amount'],
                    timestamp=r['timestamp'],
                    transactionHash=r.get('transaction_hash')
                )
                results.append(inv)
            return results

        return [inv for inv in self.investments if inv.investorAddress.lower() == address.lower()]
    
    def get_user_investments_by_id(self, user_id: int) -> List[Investment]:
        """Get all investments for a specific user by user ID."""
        results: List[Investment] = []
        if self.db:
            rows = self.db.get_investments_by_user_id(user_id)
            for r in rows:
                inv = Investment(
                    id=r.get('id'),
                    bondId=r['bond_id'],
                    investorAddress=r['investor_address'],
                    amount=r['amount'],
                    timestamp=r['timestamp'],
                    transactionHash=r.get('transaction_hash'),
                    user_id=r.get('user_id')
                )
                results.append(inv)
            return results

        return []
    
    def get_bond_investments(self, bond_id: int) -> List[Investment]:
        """Get all investments for a bond"""
        results: List[Investment] = []
        if self.db:
            rows = self.db.get_bond_investments(bond_id)
            for r in rows:
                inv = Investment(
                    bondId=r['bond_id'],
                    investorAddress=r['investor_address'],
                    amount=r['amount'],
                    timestamp=r['timestamp'],
                    transactionHash=r.get('transaction_hash')
                )
                results.append(inv)
            return results

        return [inv for inv in self.investments if inv.bondId == bond_id]
    
    def get_all_investments(self) -> List[Investment]:
        """Get all investments (persisted when DB available)."""
        results: List[Investment] = []
        if self.db:
            rows = self.db.get_all_investments()
            for r in rows:
                inv = Investment(
                    id=r.get('id'),
                    bondId=r['bond_id'],
                    investorAddress=r['investor_address'],
                    amount=r['amount'],
                    timestamp=r['timestamp'],
                    transactionHash=r.get('transaction_hash'),
                    user_id=r.get('user_id')
                )
                results.append(inv)
            return results

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
    
    # Bcrypt has a 72-byte password limit
    MAX_PASSWORD_BYTES = 72
    
    def __init__(self):
        self.db = get_db()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def _truncate_password(self, password: str) -> str:
        """Truncate password to 72 bytes (bcrypt limit)"""
        # Truncate by characters as requested (e.g. my_password[:72]).
        # This avoids passing passwords longer than the bcrypt 72-byte limit.
        if password is None:
            return password
        return password[:self.MAX_PASSWORD_BYTES]
    
    def hash_password(self, password: str) -> str:
        """Hash a password (truncates to 72 bytes first)"""
        truncated = self._truncate_password(password)
        return self.pwd_context.hash(truncated)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash (truncates to 72 bytes first)"""
        truncated = self._truncate_password(plain_password)
        return self.pwd_context.verify(truncated, hashed_password)
    
    def create_user(self, email: str, username: str, password: str) -> User:
        """Create a new user"""
        # Check if email already exists
        if self.db.get_user_by_email(email):
            raise ValueError("Email already registered")
        
        # Check if username already exists
        if self.db.get_user_by_username(username):
            raise ValueError("Username already taken")
        
        # Hash password (automatically truncated to 72 bytes)
        hashed_password = self.hash_password(password)
        
        # Create user in database
        user_data = self.db.create_user(email, username, hashed_password)
        
        return User(
            id=user_data["id"],
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=hashed_password,
            created_at=user_data["created_at"]
        )
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_data = self.db.get_user_by_email(email)
        if not user_data:
            return None
        
        return User(
            id=user_data["id"],
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=user_data["hashed_password"],
            created_at=user_data["created_at"]
        )
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        user_data = self.db.get_user_by_id(user_id)
        if not user_data:
            return None
        
        return User(
            id=user_data["id"],
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=user_data["hashed_password"],
            created_at=user_data["created_at"]
        )
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        return user



