"""
Vibe log schemas for request/response validation and serialization.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.models.vibe_log import MoodEnum, ComplexityEnum


class VibeLogBase(BaseModel):
    """Base vibe log schema with common attributes."""
    
    summary: str = Field(..., max_length=100)
    mood: MoodEnum
    energy_level: int = Field(..., ge=1, le=5)
    complexity: ComplexityEnum
    satisfaction: float = Field(..., ge=1.0, le=10.0)


class VibeLogCreateEmployee(VibeLogBase):
    """Schema for employee vibe log creation (user_id set automatically)."""
    pass


class VibeLogCreate(VibeLogBase):
    """Schema for admin vibe log creation."""
    
    user_id: int


class VibeLogUpdate(BaseModel):
    """Schema for vibe log updates."""
    
    summary: Optional[str] = Field(None, max_length=100)
    mood: Optional[MoodEnum] = None
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    complexity: Optional[ComplexityEnum] = None
    satisfaction: Optional[float] = Field(None, ge=1.0, le=10.0)


class VibeLogInDBBase(VibeLogBase):
    """Base schema for vibe logs in DB."""
    
    id: int
    user_id: int
    sentiment_rating: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class VibeLog(VibeLogInDBBase):
    """Schema for vibe log responses."""
    pass


class VibeLogInDB(VibeLogInDBBase):
    """Schema for vibe log in DB."""
    pass
