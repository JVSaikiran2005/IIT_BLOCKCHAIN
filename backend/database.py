"""
Database configuration and models for Bond Investment Platform
Uses SQLite for persistence of user credentials and investments
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

DATABASE_FILE = "bond_platform.db"


class Database:
    """Database manager for SQLite operations"""
    
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Investments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    bond_id INTEGER NOT NULL,
                    investor_address TEXT NOT NULL,
                    amount REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    transaction_hash TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_email ON users(email)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_username ON users(username)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_investment_user ON investments(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_investment_address ON investments(investor_address)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_investment_bond ON investments(bond_id)
            """)
            
            # Payment Access table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_access (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    access_level TEXT DEFAULT 'full',
                    can_invest INTEGER DEFAULT 1,
                    can_withdraw INTEGER DEFAULT 1,
                    can_transfer INTEGER DEFAULT 1,
                    payment_status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Transaction History table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    bond_id INTEGER,
                    amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    timestamp TEXT NOT NULL,
                    transaction_hash TEXT,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Transaction Bills table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER,
                    user_id INTEGER NOT NULL,
                    bond_name TEXT,
                    amount REAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    timestamp TEXT NOT NULL,
                    tax_amount REAL DEFAULT 0.0,
                    fee_amount REAL DEFAULT 0.0,
                    net_amount REAL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_payment_access_user ON payment_access(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transaction_user ON transactions(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transaction_type ON transactions(type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bill_user ON transaction_bills(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bill_status ON transaction_bills(status)
            """)
    
    def create_user(self, email: str, username: str, hashed_password: str) -> Optional[dict]:
        """Create a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                created_at = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT INTO users (email, username, hashed_password, created_at)
                    VALUES (?, ?, ?, ?)
                """, (email.lower(), username, hashed_password, created_at))
                
                user_id = cursor.lastrowid
                return {
                    "id": user_id,
                    "email": email.lower(),
                    "username": username,
                    "created_at": created_at
                }
        except sqlite3.IntegrityError as e:
            if "email" in str(e):
                raise ValueError("Email already exists")
            elif "username" in str(e):
                raise ValueError("Username already exists")
            else:
                raise ValueError(str(e))
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, username, hashed_password, created_at
                FROM users WHERE email = ?
            """, (email.lower(),))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, username, hashed_password, created_at
                FROM users WHERE id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, username, hashed_password, created_at
                FROM users WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_all_users(self) -> List[dict]:
        """Get all users"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, username, hashed_password, created_at
                FROM users
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def record_investment(self, user_id: int, bond_id: int, investor_address: str,
                         amount: float, timestamp: str, transaction_hash: Optional[str] = None) -> dict:
        """Record an investment"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO investments 
                (user_id, bond_id, investor_address, amount, timestamp, transaction_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, bond_id, investor_address, amount, timestamp, transaction_hash, created_at))
            
            investment_id = cursor.lastrowid
            return {
                "id": investment_id,
                "user_id": user_id,
                "bond_id": bond_id,
                "investor_address": investor_address,
                "amount": amount,
                "timestamp": timestamp,
                "transaction_hash": transaction_hash,
                "created_at": created_at
            }
    
    def get_user_investments(self, user_id: int) -> List[dict]:
        """Get all investments for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, bond_id, investor_address, amount, timestamp, transaction_hash, created_at
                FROM investments WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_investments_by_user_id(self, user_id: int) -> List[dict]:
        """Get all investments for a user by user ID (alias for get_user_investments)"""
        return self.get_user_investments(user_id)
    
    def get_investments_by_address(self, investor_address: str) -> List[dict]:
        """Get all investments for an address"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, bond_id, investor_address, amount, timestamp, transaction_hash, created_at
                FROM investments WHERE investor_address = ?
                ORDER BY created_at DESC
            """, (investor_address,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_bond_investments(self, bond_id: int) -> List[dict]:
        """Get all investments for a bond"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, bond_id, investor_address, amount, timestamp, transaction_hash, created_at
                FROM investments WHERE bond_id = ?
                ORDER BY created_at DESC
            """, (bond_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_all_investments(self) -> List[dict]:
        """Get all investments"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, bond_id, investor_address, amount, timestamp, transaction_hash, created_at
                FROM investments
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def create_payment_access(self, user_id: int) -> dict:
        """Create payment access record for user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO payment_access 
                (user_id, access_level, can_invest, can_withdraw, can_transfer, payment_status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, 'full', 1, 1, 1, 'active', created_at, created_at))
            
            return {
                "user_id": user_id,
                "access_level": "full",
                "can_invest": True,
                "can_withdraw": True,
                "can_transfer": True,
                "payment_status": "active",
                "created_at": created_at
            }
    
    def get_payment_access(self, user_id: int) -> Optional[dict]:
        """Get payment access for user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, access_level, can_invest, can_withdraw, can_transfer, payment_status, created_at
                FROM payment_access WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def update_payment_access(self, user_id: int, **kwargs) -> dict:
        """Update payment access for user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updated_at = datetime.now().isoformat()
            
            fields = []
            values = []
            
            if 'access_level' in kwargs:
                fields.append("access_level = ?")
                values.append(kwargs['access_level'])
            if 'can_invest' in kwargs:
                fields.append("can_invest = ?")
                values.append(1 if kwargs['can_invest'] else 0)
            if 'can_withdraw' in kwargs:
                fields.append("can_withdraw = ?")
                values.append(1 if kwargs['can_withdraw'] else 0)
            if 'can_transfer' in kwargs:
                fields.append("can_transfer = ?")
                values.append(1 if kwargs['can_transfer'] else 0)
            if 'payment_status' in kwargs:
                fields.append("payment_status = ?")
                values.append(kwargs['payment_status'])
            
            if not fields:
                return self.get_payment_access(user_id) or {}
            
            fields.append("updated_at = ?")
            values.append(updated_at)
            values.append(user_id)
            
            cursor.execute(f"""
                UPDATE payment_access 
                SET {', '.join(fields)}
                WHERE user_id = ?
            """, values)
            
            return self.get_payment_access(user_id) or {}
    
    def get_all_payment_access(self) -> List[dict]:
        """Get payment access for all users"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pa.id, pa.user_id, u.username, u.email, pa.access_level, 
                       pa.can_invest, pa.can_withdraw, pa.can_transfer, pa.payment_status, pa.created_at
                FROM payment_access pa
                JOIN users u ON pa.user_id = u.id
                ORDER BY pa.created_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def record_transaction(self, user_id: int, trans_type: str, amount: float, 
                          bond_id: Optional[int] = None, status: str = 'pending',
                          transaction_hash: Optional[str] = None, description: Optional[str] = None) -> dict:
        """Record a transaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO transactions 
                (user_id, type, bond_id, amount, status, timestamp, transaction_hash, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, trans_type, bond_id, amount, status, timestamp, transaction_hash, description, created_at))
            
            transaction_id = cursor.lastrowid
            return {
                "id": transaction_id,
                "user_id": user_id,
                "type": trans_type,
                "bond_id": bond_id,
                "amount": amount,
                "status": status,
                "timestamp": timestamp,
                "transaction_hash": transaction_hash,
                "description": description,
                "created_at": created_at
            }
    
    def get_user_transactions(self, user_id: int) -> List[dict]:
        """Get all transactions for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, type, bond_id, amount, status, timestamp, transaction_hash, description, created_at
                FROM transactions WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_all_transactions(self) -> List[dict]:
        """Get all transactions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.user_id, u.username, u.email, t.type, t.bond_id, t.amount, 
                       t.status, t.timestamp, t.transaction_hash, t.description, t.created_at
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                ORDER BY t.created_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def create_transaction_bill(self, transaction_id: Optional[int], user_id: int, 
                               bond_name: Optional[str], amount: float, trans_type: str,
                               status: str = 'pending', tax_amount: float = 0.0, 
                               fee_amount: float = 0.0) -> dict:
        """Create a transaction bill"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            created_at = datetime.now().isoformat()
            net_amount = amount - tax_amount - fee_amount
            
            cursor.execute("""
                INSERT INTO transaction_bills 
                (transaction_id, user_id, bond_name, amount, transaction_type, status, 
                 timestamp, tax_amount, fee_amount, net_amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (transaction_id, user_id, bond_name, amount, trans_type, status,
                  timestamp, tax_amount, fee_amount, net_amount, created_at))
            
            return {
                "id": cursor.lastrowid,
                "transaction_id": transaction_id,
                "user_id": user_id,
                "bond_name": bond_name,
                "amount": amount,
                "transaction_type": trans_type,
                "status": status,
                "timestamp": timestamp,
                "tax_amount": tax_amount,
                "fee_amount": fee_amount,
                "net_amount": net_amount,
                "created_at": created_at
            }
    
    def get_user_bills(self, user_id: int) -> List[dict]:
        """Get all bills for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, transaction_id, user_id, bond_name, amount, transaction_type, status,
                       timestamp, tax_amount, fee_amount, net_amount, created_at
                FROM transaction_bills WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_all_bills(self) -> List[dict]:
        """Get all transaction bills"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tb.id, tb.transaction_id, tb.user_id, u.username, u.email, tb.bond_name, 
                       tb.amount, tb.transaction_type, tb.status, tb.timestamp, tb.tax_amount, 
                       tb.fee_amount, tb.net_amount, tb.created_at
                FROM transaction_bills tb
                JOIN users u ON tb.user_id = u.id
                ORDER BY tb.created_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def delete_database(self):
        """Delete database file (for testing)"""
        if os.path.exists(self.db_file):
            os.remove(self.db_file)


# Global database instance
_db: Optional[Database] = None


def get_db() -> Database:
    """Get or create the database instance"""
    global _db
    if _db is None:
        _db = Database()
    return _db


def init_db_instance():
    """Initialize database instance"""
    global _db
    _db = Database()
    return _db
