"""
Token schemas for authentication.
"""
from typing import List, Optional

from pydantic import BaseModel


class Token(BaseModel):
    """Token schema for authentication responses."""
    
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token payload schema."""
    
    sub: Optional[str] = None
    user_id: Optional[int] = None
    scopes: List[str] = []
    exp: Optional[int] = None
