"""
Authentication & Authorization Module for CrystaGraph.
Handles JWT token generation, secure password hashing, and user authentication dependencies.
"""

import os
import sys
import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from components.db_utils import get_connection

SECRET_KEY = os.environ.get("CRYSTAGRAPH_JWT_SECRET", "crystagraph_academic_jwt_secret_key_2026_bmu")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days for academic sessions
PASSWORD_SALT = "crystagraph_academic_salt_2026"

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hashes password with cryptographic salt using SHA-256."""
    return hashlib.sha256((password + PASSWORD_SALT).encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against stored salted hash."""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT bearer token with expiration timestamp."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and verifies JWT token signature and expiry."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """Dependency for strictly protected endpoints. Raises 401 if token invalid."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload["sub"]
    
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            SELECT user_id, email, full_name, institution, department, role, created_at
            FROM users WHERE user_id = ?;
        """, (user_id,))
        row = c.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account not found")
        
        return {
            "user_id": row[0],
            "email": row[1],
            "full_name": row[2],
            "institution": row[3],
            "department": row[4],
            "role": row[5],
            "created_at": row[6]
        }
    finally:
        conn.close()

def get_optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Dependency for endpoints allowing both public and authenticated queries."""
    if not credentials:
        return None
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None
