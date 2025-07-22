"""
Role-Based Access Control (RBAC) middleware for authorization.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers.user_controller import user_controller
from app.middlewares.auth_middleware import get_current_user, TokenData
from app.models.user import User


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current active user from database.
    
    Args:
        current_user: Token data from JWT
        db: Database session
        
    Returns:
        User model instance
        
    Raises:
        HTTPException: If user not found or inactive
    """
    if not current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token"
        )
    
    user = user_controller.get(db, id=current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Verify current user is a superuser (admin/HR).
    
    Args:
        current_user: Current active user
        
    Returns:
        User model instance
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Superuser access required."
        )
    
    return current_user


def verify_user_access(requested_user_id: int, current_user: User) -> bool:
    """
    Verify if current user can access data for requested user ID.
    
    Args:
        requested_user_id: ID of user whose data is being accessed
        current_user: Current authenticated user
        
    Returns:
        True if access is allowed, False otherwise
    """
    # Superusers can access any user's data
    if current_user.is_superuser:
        return True
    
    # Regular users can only access their own data
    return current_user.id == requested_user_id


async def verify_user_or_superuser_access(
    user_id: int,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Verify user can access data for specified user_id (own data or superuser).
    
    Args:
        user_id: ID of user whose data is being accessed
        current_user: Current authenticated user
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If access is denied
    """
    if not verify_user_access(user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this user's data"
        )
    
    return current_user
