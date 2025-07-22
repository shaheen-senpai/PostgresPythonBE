"""
Pydantic schemas for sentiment rating operations.
"""
from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

from app.models.sentiment_rating import MoodEnum, ComplexityEnum


class SentimentRatingInput(BaseModel):
    """Schema for sentiment rating input data."""
    user_id: int = Field(..., description="User ID (foreign key)")
    summary: str = Field(..., max_length=100, description="Summary of the user's situation")
    mood: MoodEnum = Field(..., description="User's current mood")
    energy_level: int = Field(..., ge=1, le=5, description="Energy level on 1-5 scale")
    complexity: ComplexityEnum = Field(..., description="Complexity level of the situation")
    satisfaction: float = Field(..., ge=1.0, le=10.0, description="Satisfaction level on 1-10 scale")
    
    @validator('energy_level')
    def validate_energy_level(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Energy level must be between 1 and 5')
        return v
    
    @validator('satisfaction')
    def validate_satisfaction(cls, v):
        if not 1.0 <= v <= 10.0:
            raise ValueError('Satisfaction must be between 1.0 and 10.0')
        return v


class SentimentRatingAIResponse(BaseModel):
    """Schema for AI generated sentiment rating response."""
    user_id: int = Field(..., description="User ID (foreign key)")
    sentiment_rating: float = Field(..., ge=0.0, le=100.0, description="AI generated sentiment rating out of 100")
    
    @validator('sentiment_rating')
    def validate_sentiment_rating(cls, v):
        if not 0.0 <= v <= 100.0:
            raise ValueError('Sentiment rating must be between 0.0 and 100.0')
        return v


class SentimentRatingOutput(BaseModel):
    """Schema for sentiment rating output (database record)."""
    id: int
    user_id: int
    summary: str
    mood: MoodEnum
    energy_level: int
    complexity: ComplexityEnum
    satisfaction: float
    sentiment_rating: float
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SentimentRatingCreate(BaseModel):
    """Schema for creating a new sentiment rating record."""
    user_id: int
    summary: str
    mood: MoodEnum
    energy_level: int
    complexity: ComplexityEnum
    satisfaction: float
    sentiment_rating: float


class SentimentRatingUpdate(BaseModel):
    """Schema for updating a sentiment rating record."""
    summary: Optional[str] = Field(None, max_length=100)
    mood: Optional[MoodEnum] = None
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    complexity: Optional[ComplexityEnum] = None
    satisfaction: Optional[float] = Field(None, ge=1.0, le=10.0)
    sentiment_rating: Optional[float] = Field(None, ge=0.0, le=100.0) 