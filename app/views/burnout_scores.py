"""
Burnout scores API endpoints with role-based access control (superuser only).
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers.burnout_score_controller import burnout_score_controller
from app.middlewares.rbac import get_current_superuser
from app.models.user import User
from app.schemas.burnout_score import BurnoutScore, BurnoutScoreCreate, BurnoutScoreUpdate

router = APIRouter()


@router.get("/user/{user_id}", response_model=List[BurnoutScore])
def get_user_burnout_scores(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get burnout scores for a specific user.
    
    Employee access: ❌ Forbidden
    Admin access: ✅ Any user's burnout scores
    """
    return burnout_score_controller.get_by_user_id(
        db=db, 
        user_id=user_id, 
        skip=skip, 
        limit=limit
    )


@router.get("/all", response_model=List[BurnoutScore])
def get_all_burnout_scores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get all burnout scores from all users.
    
    Employee access: ❌ Forbidden
    Admin access: ✅ All users' burnout scores
    """
    return burnout_score_controller.get_all_scores(
        db=db, 
        skip=skip, 
        limit=limit
    )


@router.post("/", response_model=BurnoutScore)
def create_burnout_score(
    burnout_score_in: BurnoutScoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Create a new burnout score.
    
    Employee access: ❌ Forbidden
    Admin access: ✅ Create burnout scores for any user
    """
    return burnout_score_controller.create_for_user(
        db=db,
        obj_in=burnout_score_in
    )


@router.get("/{burnout_score_id}", response_model=BurnoutScore)
def get_burnout_score(
    burnout_score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get a specific burnout score by ID.
    
    Employee access: ❌ Forbidden
    Admin access: ✅ Any burnout score
    """
    burnout_score = burnout_score_controller.get(db=db, id=burnout_score_id)
    if not burnout_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Burnout score not found"
        )
    
    return burnout_score


@router.put("/{burnout_score_id}", response_model=BurnoutScore)
def update_burnout_score(
    burnout_score_id: int,
    burnout_score_update: BurnoutScoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Update a burnout score.
    
    Employee access: ❌ Forbidden
    Admin access: ✅ Any burnout score
    """
    burnout_score = burnout_score_controller.get(db=db, id=burnout_score_id)
    if not burnout_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Burnout score not found"
        )
    
    return burnout_score_controller.update(
        db=db,
        db_obj=burnout_score,
        obj_in=burnout_score_update
    )


@router.delete("/{burnout_score_id}", response_model=BurnoutScore)
def delete_burnout_score(
    burnout_score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Delete a burnout score.
    
    Employee access: ❌ Forbidden
    Admin access: ✅ Any burnout score
    """
    burnout_score = burnout_score_controller.get(db=db, id=burnout_score_id)
    if not burnout_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Burnout score not found"
        )
    
    return burnout_score_controller.remove(db=db, id=burnout_score_id)
