"""
Vibe log model for tracking user mood and energy levels.
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class MoodEnum(enum.Enum):
    """Mood enumeration."""
    SAD = "sad"
    ANGRY = "angry"
    HAPPY = "happy"
    GOOD = "good"
    EXCITED = "excited"


class ComplexityEnum(enum.Enum):
    """Complexity enumeration."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class VibeLog(BaseModel):
    """Vibe log model for tracking user mood and energy levels."""
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Vibe log fields
    summary = Column(String(100), nullable=False)
    mood = Column(Enum(MoodEnum), nullable=False)
    energy_level = Column(Integer, nullable=False)  # 1-5 scale
    complexity = Column(Enum(ComplexityEnum), nullable=False)
    satisfaction = Column(Float, nullable=False)  # 1-10 scale
    sentiment_rating = Column(Float, nullable=True)  # AI generated, out of 100
    
    # Relationships
    user = relationship("User", back_populates="vibe_logs")
    
    # Table arguments for indexes
    __table_args__ = (
        Index('idx_vibe_log_user_id', 'user_id'),
        Index('idx_vibe_log_created_at', 'created_at'),
        Index('idx_vibe_log_mood', 'mood'),
        Index('idx_vibe_log_energy_level', 'energy_level'),
    )
    
    def __repr__(self) -> str:
        """String representation of the vibe log."""
        return f"<VibeLog {self.id}: {self.mood.value} - {self.energy_level}/5>"
