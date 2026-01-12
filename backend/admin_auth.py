"""
Admin Authentication utilities for JWT token management
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import User
from services import UserService

# JWT Configuration for Admin
ADMIN_SECRET_KEY = "admin-secret-key-change-this-in-production"  # In production, use environment variable
ADMIN_ALGORITHM = "HS256"
ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

# Hardcoded admin credentials (in production, use database with secure admin table)
ADMIN_CREDENTIALS = {
    "admin@government.com": "admin123",  # Change these!
    "administrator@bonds.com": "secure_password_123"
}


def create_admin_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token for admin"""
    to_encode = data.copy()
    if 'sub' in to_encode and not isinstance(to_encode['sub'], str):
        to_encode['sub'] = str(to_encode['sub'])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "admin": True})
    encoded_jwt = jwt.encode(to_encode, ADMIN_SECRET_KEY, algorithm=ADMIN_ALGORITHM)
    return encoded_jwt


def verify_admin_token(token: str) -> dict:
    """Verify and decode an admin JWT token"""
    try:
        payload = jwt.decode(token, ADMIN_SECRET_KEY, algorithms=[ADMIN_ALGORITHM])
        if not payload.get("admin"):
            raise JWTError("Not an admin token")
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get the current authenticated admin"""
    token = credentials.credentials
    payload = verify_admin_token(token)
    admin_email = payload.get("sub")
    
    if admin_email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "email": admin_email,
        "user_id": payload.get("user_id"),
        "username": payload.get("username")
    }


def authenticate_admin(email: str, password: str) -> Optional[dict]:
    """Authenticate admin with email and password"""
    if email in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[email] == password:
        return {
            "email": email,
            "username": email.split('@')[0],
            "user_id": 0  # Admin user ID
        }
    return None
