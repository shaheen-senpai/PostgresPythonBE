"""
User routes for user management.
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers.user_controller import user_controller
from app.middlewares.auth_middleware import get_current_user, TokenData
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> Any:
    """
    Retrieve users with pagination.
    """
    # Check if user has admin scope
    if "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    users = user_controller.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Create new user.
    """
    user = user_controller.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=User)
async def read_user_me(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    user = user_controller.get_by_username(db, username=current_user.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> Any:
    """
    Update current user.
    """
    user = user_controller.get_by_username(db, username=current_user.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user = user_controller.update(db, db_obj=user, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=User)
async def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> Any:
    """
    Get user by ID.
    """
    # Check if user is requesting their own info or has admin scope
    is_admin = "admin" in current_user.scopes
    is_same_user = current_user.user_id == user_id
    
    if not (is_admin or is_same_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    user = user_controller.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user
