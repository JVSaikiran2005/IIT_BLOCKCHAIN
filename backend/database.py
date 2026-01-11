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
