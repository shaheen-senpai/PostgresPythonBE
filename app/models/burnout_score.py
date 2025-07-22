"""
Burnout score model for tracking user burnout levels (super admin only).
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class BurnoutScore(BaseModel):
    """Burnout score model for tracking user burnout levels."""
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Burnout score fields
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    burnout_score = Column(Float, nullable=False)  # AI generated, out of 100
    
    # Relationships
    user = relationship("User", back_populates="burnout_scores")
    
    # Table arguments for indexes
    __table_args__ = (
        Index('idx_burnout_score_user_id', 'user_id'),
        Index('idx_burnout_score_period_start', 'period_start'),
        Index('idx_burnout_score_period_end', 'period_end'),
        Index('idx_burnout_score_created_at', 'created_at'),
        Index('idx_burnout_score_value', 'burnout_score'),
    )
    
    def __repr__(self) -> str:
        """String representation of the burnout score."""
        return f"<BurnoutScore {self.id}: {self.burnout_score}/100>"
