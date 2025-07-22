"""
Burnout score schemas for request/response validation and serialization.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BurnoutScoreBase(BaseModel):
    """Base burnout score schema with common attributes."""
    
    period_start: datetime
    period_end: datetime
    burnout_score: float = Field(..., ge=0.0, le=100.0)


class BurnoutScoreCreate(BurnoutScoreBase):
    """Schema for burnout score creation."""
    
    user_id: int


class BurnoutScoreUpdate(BaseModel):
    """Schema for burnout score updates."""
    
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    burnout_score: Optional[float] = Field(None, ge=0.0, le=100.0)


class BurnoutScoreInDBBase(BurnoutScoreBase):
    """Base schema for burnout scores in DB."""
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class BurnoutScore(BurnoutScoreInDBBase):
    """Schema for burnout score responses."""
    pass


class BurnoutScoreInDB(BurnoutScoreInDBBase):
    """Schema for burnout score in DB."""
    pass
