from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db # Assuming get_db is available in database.py
from . import models
# Security Configuration
SECRET_KEY = "your-secret-key"  # IMPORTANT: Change this in a real application
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Define the hashing context using bcrypt
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Function to get the hashed password for storage
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Function to verify a password against a stored hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Function to create a JWT access token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Decodes JWT, finds the user in the DB, and raises 401 on failure."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Pull the user from the database
        user = db.query(models.User).filter(models.User.username == username).first()
        if user is None:
            raise credentials_exception
            
        return user
        
    except Exception:
        raise credentials_exception

def check_role(required_role: str):
    """Dependency checker that ensures the current user has the required role."""
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User must have the role '{required_role}' to perform this action"
            )
        return current_user
    return role_checker