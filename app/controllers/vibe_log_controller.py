"""
Vibe log controller for CRUD operations.
"""
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app.controllers.base_controller import BaseController
from app.models.vibe_log import VibeLog
from app.schemas.vibe_log import VibeLogCreate, VibeLogUpdate
from app.services.background_tasks import process_vibe_log_sentiment, create_vibe_log_data_dict


class VibeLogController(BaseController[VibeLog, VibeLogCreate, VibeLogUpdate]):
    """Controller for vibe log operations."""
    
    def get_by_user_id(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[VibeLog]:
        """
        Get vibe logs for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of vibe logs for the user
        """
        return (
            db.query(VibeLog)
            .filter(VibeLog.user_id == user_id)
            .filter(VibeLog.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_all_logs(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[VibeLog]:
        """
        Get all vibe logs (superuser only).
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of all vibe logs
        """
        return (
            db.query(VibeLog)
            .filter(VibeLog.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_for_user(
        self, 
        db: Session, 
        obj_in: VibeLogCreate, 
        user_id: int
    ) -> VibeLog:
        """
        Create a vibe log for a specific user.
        
        Args:
            db: Database session
            obj_in: Vibe log creation data
            user_id: User ID to associate with the log
            
        Returns:
            Created vibe log
        """
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = VibeLog(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_for_user_with_ai_sentiment(
        self, 
        db: Session, 
        obj_in: VibeLogCreate, 
        user_id: int,
        background_tasks: BackgroundTasks
    ) -> VibeLog:
        """
        Create a vibe log for a specific user with AI sentiment analysis.
        
        Args:
            db: Database session
            obj_in: Vibe log creation data
            user_id: User ID to associate with the log
            background_tasks: FastAPI background tasks
            
        Returns:
            Created vibe log (sentiment_rating will be updated asynchronously by AI)
        """
        # Create vibe log first (without sentiment)
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        obj_in_data["sentiment_rating"] = None  # Will be updated by AI background task
        
        db_obj = VibeLog(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Prepare data for AI sentiment analysis
        vibe_log_data = create_vibe_log_data_dict(db_obj)
        
        # Add background task for AI sentiment analysis
        background_tasks.add_task(
            process_vibe_log_sentiment,
            vibe_log_id=db_obj.id,
            vibe_log_data=vibe_log_data
        )
        
        return db_obj


# Create instance
vibe_log_controller = VibeLogController(VibeLog)
