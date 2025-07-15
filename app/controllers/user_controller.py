"""
User controller for user management operations.
"""
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.controllers.base_controller import BaseController
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash, verify_password


class UserController(BaseController[User, UserCreate, UserUpdate]):
    """Controller for user operations."""
    
    def __init__(self):
        """Initialize with User model."""
        super().__init__(User)
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            db: Database session
            username: Username
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.username == username).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create new user with hashed password.
        
        Args:
            db: Database session
            obj_in: User creation data
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email already exists
        if self.get_by_email(db, email=obj_in.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Check if username already exists
        if self.get_by_username(db, username=obj_in.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
        
        # Create user with hashed password
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            full_name=obj_in.full_name,
            hashed_password=get_password_hash(obj_in.password),
            is_active=True,
            is_superuser=obj_in.is_superuser if hasattr(obj_in, "is_superuser") else False,
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """
        Authenticate user by username and password.
        
        Args:
            db: Database session
            username: Username
            password: Plain password
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser."""
        return user.is_superuser


# Create singleton instance
user_controller = UserController()
