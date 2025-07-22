"""
Vibe report schemas for request/response validation and serialization.
"""
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel


class VibeReportBase(BaseModel):
    """Base vibe report schema with common attributes."""
    
    period_start: datetime
    period_end: datetime
    report_data: Dict[str, Any]


class VibeReportCreate(VibeReportBase):
    """Schema for vibe report creation."""
    
    user_id: int
    generated_by: int


class VibeReportUpdate(BaseModel):
    """Schema for vibe report updates."""
    
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    report_data: Optional[Dict[str, Any]] = None


class VibeReportInDBBase(VibeReportBase):
    """Base schema for vibe reports in DB."""
    
    id: int
    user_id: int
    generated_by: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class VibeReport(VibeReportInDBBase):
    """Schema for vibe report responses."""
    pass


class VibeReportInDB(VibeReportInDBBase):
    """Schema for vibe report in DB."""
    pass
