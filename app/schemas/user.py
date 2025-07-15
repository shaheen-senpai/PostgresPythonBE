"""
User schemas for request/response validation and serialization.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(UserBase):
    """Schema for user creation."""
    
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username is alphanumeric."""
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v


class UserUpdate(UserBase):
    """Schema for user updates."""
    
    password: Optional[str] = Field(None, min_length=8)


class UserInDBBase(UserBase):
    """Base schema for users in DB."""
    
    id: int
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class User(UserInDBBase):
    """Schema for user responses."""
    pass


class UserInDB(UserInDBBase):
    """Schema for user in DB with hashed password."""
    
    hashed_password: str
