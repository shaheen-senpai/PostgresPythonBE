"""
Base model with common fields and methods for all models.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, Integer, Index
from sqlalchemy.ext.declarative import declared_attr

from app.config.database import Base


class BaseModel(Base):
    """Base model with common fields and methods."""
    
    # Make this class abstract so it's not created as a table
    __abstract__ = True
    
    # Auto-generate table name from class name
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'
    
    # Common columns for all models
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Any:
        """Create model instance from dictionary."""
        return cls(**data)
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
