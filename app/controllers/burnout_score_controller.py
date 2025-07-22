"""
Burnout score controller for CRUD operations (superuser only).
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.controllers.base_controller import BaseController
from app.models.burnout_score import BurnoutScore
from app.schemas.burnout_score import BurnoutScoreCreate, BurnoutScoreUpdate


class BurnoutScoreController(BaseController[BurnoutScore, BurnoutScoreCreate, BurnoutScoreUpdate]):
    """Controller for burnout score operations (superuser only)."""
    
    def get_by_user_id(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[BurnoutScore]:
        """
        Get burnout scores for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of burnout scores for the user
        """
        return (
            db.query(BurnoutScore)
            .filter(BurnoutScore.user_id == user_id)
            .filter(BurnoutScore.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_all_scores(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[BurnoutScore]:
        """
        Get all burnout scores (superuser only).
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of all burnout scores
        """
        return (
            db.query(BurnoutScore)
            .filter(BurnoutScore.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_for_user(
        self, 
        db: Session, 
        obj_in: BurnoutScoreCreate
    ) -> BurnoutScore:
        """
        Create a burnout score for a user.
        
        Args:
            db: Database session
            obj_in: Burnout score creation data
            
        Returns:
            Created burnout score
        """
        obj_in_data = obj_in.dict()
        db_obj = BurnoutScore(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create instance
burnout_score_controller = BurnoutScoreController(BurnoutScore)
