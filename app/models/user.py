"""
User model for authentication and user management.
"""
from sqlalchemy import Column, String, Boolean, Index
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """User model for authentication and user management."""
    
    # User fields
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Relationships can be added here, for example:
    # posts = relationship("Post", back_populates="author")
    
    # Table arguments for indexes
    __table_args__ = (
        # GIN indexes with trigram operators for partial ILIKE searches
        Index('idx_username_gin_trgm', 'username', 
              postgresql_using='gin', 
              postgresql_ops={'username': 'gin_trgm_ops'}),
        Index('idx_email_gin_trgm', 'email', 
              postgresql_using='gin', 
              postgresql_ops={'email': 'gin_trgm_ops'}),
        Index('idx_full_name_gin_trgm', 'full_name', 
              postgresql_using='gin', 
              postgresql_ops={'full_name': 'gin_trgm_ops'}),
        # Keep unique indexes for exact lookups (these are automatically created by unique=True)
        # But we can also add regular B-tree indexes for exact matches if needed
        Index('idx_username_btree', 'username'),
        Index('idx_email_btree', 'email'),
    )
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User {self.username}>"
