"""
Vibe report model for storing AI-generated reports.
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class VibeReport(BaseModel):
    """Vibe report model for storing AI-generated reports."""
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    generated_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Report fields
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    report_data = Column(JSONB, nullable=False)  # AI generated report data
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="vibe_reports")
    generator = relationship("User", foreign_keys=[generated_by])
    
    # Table arguments for indexes
    __table_args__ = (
        Index('idx_vibe_report_user_id', 'user_id'),
        Index('idx_vibe_report_generated_by', 'generated_by'),
        Index('idx_vibe_report_period_start', 'period_start'),
        Index('idx_vibe_report_period_end', 'period_end'),
        Index('idx_vibe_report_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        """String representation of the vibe report."""
        return f"<VibeReport {self.id}: {self.period_start} to {self.period_end}>"
