"""
Authentication middleware for JWT token validation.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


class TokenData(BaseModel):
    """Token data model."""
    
    username: Optional[str] = None
    user_id: Optional[int] = None
    scopes: list[str] = []


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    # Create JWT token
    encoded_jwt = jwt.encode(
        to_encode, 
        get_settings().SECRET_KEY, 
        algorithm=get_settings().ALGORITHM
    )
    
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Validate JWT token and extract user data.
    
    Args:
        token: JWT token
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            get_settings().SECRET_KEY, 
            algorithms=[get_settings().ALGORITHM]
        )
        
        # Extract user data
        username = payload.get("sub")
        user_id = payload.get("user_id")
        scopes = payload.get("scopes", [])
        
        if username is None:
            logger.warning("Token missing username claim")
            raise credentials_exception
            
        # Create token data
        token_data = TokenData(
            username=username,
            user_id=user_id,
            scopes=scopes
        )
        
        return token_data
        
    except JWTError as e:
        logger.warning(f"JWT validation error: {str(e)}")
        raise credentials_exception
