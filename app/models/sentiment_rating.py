"""
Sentiment Rating model for storing user mood analysis results.
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.vibe_log import ComplexityEnum, MoodEnum

class SentimentRating(BaseModel):
    """Sentiment Rating model for storing user mood analysis results."""
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Input fields for analysis
    summary = Column(String(100), nullable=False)
    mood = Column(Enum(MoodEnum), nullable=False)
    energy_level = Column(Integer, nullable=False)  # 1-5 scale
    complexity = Column(Enum(ComplexityEnum), nullable=False)
    satisfaction = Column(Float, nullable=False)  # 1-10 scale
    
    # AI generated output
    sentiment_rating = Column(Float, nullable=False)  # out of 100
    
    # Relationships
    user = relationship("User", backref="sentiment_ratings")
    
    # Table arguments for indexes
    __table_args__ = (
        # Index on user_id for efficient queries
        Index('idx_sentiment_user_id', 'user_id'),
        # Index on sentiment_rating for analytics
        Index('idx_sentiment_rating', 'sentiment_rating'),
        # Composite index for user queries with filtering
        Index('idx_user_sentiment_created', 'user_id', 'sentiment_rating', 'created_at'),
    )
    
    def __repr__(self) -> str:
        """String representation of the sentiment rating."""
        return f"<SentimentRating user_id={self.user_id} rating={self.sentiment_rating}>" 