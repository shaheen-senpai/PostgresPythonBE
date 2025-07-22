"""
Vibe report controller for CRUD operations.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.controllers.base_controller import BaseController
from app.models.vibe_report import VibeReport
from app.schemas.vibe_report import VibeReportCreate, VibeReportUpdate


class VibeReportController(BaseController[VibeReport, VibeReportCreate, VibeReportUpdate]):
    """Controller for vibe report operations."""
    
    def get_by_user_id(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[VibeReport]:
        """
        Get vibe reports for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of vibe reports for the user
        """
        return (
            db.query(VibeReport)
            .filter(VibeReport.user_id == user_id)
            .filter(VibeReport.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_all_reports(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[VibeReport]:
        """
        Get all vibe reports (superuser only).
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of all vibe reports
        """
        return (
            db.query(VibeReport)
            .filter(VibeReport.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_for_user(
        self, 
        db: Session, 
        obj_in: VibeReportCreate, 
        generated_by_user_id: int
    ) -> VibeReport:
        """
        Create a vibe report.
        
        Args:
            db: Database session
            obj_in: Vibe report creation data
            generated_by_user_id: User ID who generated the report
            
        Returns:
            Created vibe report
        """
        obj_in_data = obj_in.dict()
        obj_in_data["generated_by"] = generated_by_user_id
        db_obj = VibeReport(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create instance
vibe_report_controller = VibeReportController(VibeReport)
