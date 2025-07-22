"""
Vibe logs API endpoints with role-based access control.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers.vibe_log_controller import vibe_log_controller
from app.middlewares.rbac import (
    get_current_active_user,
    get_current_superuser,
    verify_user_or_superuser_access
)
from app.models.user import User
from app.schemas.vibe_log import VibeLog, VibeLogCreate, VibeLogCreateEmployee, VibeLogUpdate

router = APIRouter()


@router.get("/me", response_model=List[VibeLog])
def get_my_vibe_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user's vibe logs.
    
    Employee access: Own data only
    Admin access: Own data only (when using this endpoint)
    """
    return vibe_log_controller.get_by_user_id(
        db=db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit
    )


@router.get("/user/{user_id}", response_model=List[VibeLog])
def get_user_vibe_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_user_or_superuser_access),
):
    """
    Get vibe logs for a specific user.
    
    Employee access: Own data only (user_id must match current user)
    Admin access: Any user's data
    """
    return vibe_log_controller.get_by_user_id(
        db=db, 
        user_id=user_id, 
        skip=skip, 
        limit=limit
    )


@router.get("/all", response_model=List[VibeLog])
def get_all_vibe_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get all vibe logs from all users.
    
    Employee access: Forbidden
    Admin access: All users' data
    """
    return vibe_log_controller.get_all_logs(
        db=db, 
        skip=skip, 
        limit=limit
    )


@router.post("/", response_model=VibeLog)
def create_vibe_log(
    vibe_log_in: VibeLogCreateEmployee,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new vibe log for current user with AI sentiment analysis.
    
    Employee access: Create own vibe logs
    Admin access: Create vibe logs for themselves
    
    Note: AI sentiment analysis runs in background - sentiment_rating will be updated asynchronously
    """
    return vibe_log_controller.create_for_user_with_ai_sentiment(
        db=db,
        obj_in=vibe_log_in,
        user_id=current_user.id,
        background_tasks=background_tasks
    )


@router.post("/admin", response_model=VibeLog)
def create_vibe_log_admin(
    vibe_log_in: VibeLogCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Create a new vibe log for any user (admin only) with AI sentiment analysis.
    
    Employee access: Forbidden
    Admin access: Create vibe logs for any user
    
    Note: AI sentiment analysis runs in background - sentiment_rating will be updated asynchronously
    """
    return vibe_log_controller.create_for_user_with_ai_sentiment(
        db=db,
        obj_in=vibe_log_in,
        user_id=vibe_log_in.user_id,
        background_tasks=background_tasks
    )


@router.post("/no-sentiment", response_model=VibeLog)
def create_vibe_log_no_sentiment(
    vibe_log_in: VibeLogCreateEmployee,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new vibe log without AI sentiment analysis (fallback endpoint).
    
    Employee access: Create own vibe logs
    Admin access: Create vibe logs for themselves
    """
    return vibe_log_controller.create_for_user(
        db=db,
        obj_in=vibe_log_in,
        user_id=current_user.id
    )


@router.get("/{vibe_log_id}", response_model=VibeLog)
def get_vibe_log(
    vibe_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific vibe log by ID.
    
    Employee access: Own vibe logs only
    Admin access: Any vibe log
    """
    vibe_log = vibe_log_controller.get(db=db, id=vibe_log_id)
    if not vibe_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vibe log not found"
        )
    
    # Check access permissions
    if not current_user.is_superuser and vibe_log.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this vibe log"
        )
    
    return vibe_log


@router.put("/{vibe_log_id}", response_model=VibeLog)
def update_vibe_log(
    vibe_log_id: int,
    vibe_log_update: VibeLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a vibe log.
    
    Employee access: Own vibe logs only
    Admin access: Any vibe log
    """
    vibe_log = vibe_log_controller.get(db=db, id=vibe_log_id)
    if not vibe_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vibe log not found"
        )
    
    # Check access permissions
    if not current_user.is_superuser and vibe_log.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this vibe log"
        )
    
    return vibe_log_controller.update(
        db=db,
        db_obj=vibe_log,
        obj_in=vibe_log_update
    )


@router.delete("/{vibe_log_id}", response_model=VibeLog)
def delete_vibe_log(
    vibe_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a vibe log.
    
    Employee access: Own vibe logs only
    Admin access: Any vibe log
    """
    vibe_log = vibe_log_controller.get(db=db, id=vibe_log_id)
    if not vibe_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vibe log not found"
        )
    
    # Check access permissions
    if not current_user.is_superuser and vibe_log.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this vibe log"
        )
    
    return vibe_log_controller.remove(db=db, id=vibe_log_id)
