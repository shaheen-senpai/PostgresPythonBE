"""
Base controller with common methods for all controllers.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.base import BaseModel as DBBaseModel

# Define generic types for models and schemas
ModelType = TypeVar("ModelType", bound=DBBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseController(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base controller with CRUD operations for working with SQLAlchemy models.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize with the SQLAlchemy model class.
        
        Args:
            model: The SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Record if found, None otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_attribute(self, db: Session, attr_name: str, attr_value: Any) -> Optional[ModelType]:
        """
        Get a single record by attribute.
        
        Args:
            db: Database session
            attr_name: Attribute name
            attr_value: Attribute value
            
        Returns:
            Record if found, None otherwise
        """
        return db.query(self.model).filter(getattr(self.model, attr_name) == attr_value).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of records
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Input data
            
        Returns:
            Created record
        """
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        Update a record.
        
        Args:
            db: Database session
            db_obj: Database object to update
            obj_in: Input data
            
        Returns:
            Updated record
        """
        obj_data = db_obj.to_dict()
        update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        Delete a record.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Deleted record
            
        Raises:
            HTTPException: If record not found
        """
        obj = db.query(self.model).get(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id {id} not found"
            )
        db.delete(obj)
        db.commit()
        return obj
