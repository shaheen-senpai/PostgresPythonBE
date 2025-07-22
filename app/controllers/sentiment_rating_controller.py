"""
Sentiment Rating Controller for handling sentiment analysis operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.ai.sentiment_rating_service import get_sentiment_rating_service
from app.models.sentiment_rating import SentimentRating
from app.schemas.sentiment_rating import (
    SentimentRatingInput, 
    SentimentRatingOutput, 
    SentimentRatingCreate,
    SentimentRatingAIResponse
)
from app.controllers.base_controller import BaseController
from app.utils.logger import logger


class SentimentRatingController(BaseController):
    """Controller for sentiment rating operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, SentimentRating)
        self.sentiment_service = get_sentiment_rating_service()
    
    async def analyze_and_create_sentiment_rating(
        self, 
        input_data: SentimentRatingInput,
        model: str = "gemini-1.5-pro"
    ) -> SentimentRatingOutput:
        """
        Analyze sentiment using AI and create a database record.
        
        Args:
            input_data: The input data for sentiment analysis
            model: AI model to use for analysis
            
        Returns:
            SentimentRatingOutput with the created record
            
        Raises:
            Exception: If analysis or database operation fails
        """
        try:
            # Generate sentiment rating using AI service
            ai_response: SentimentRatingAIResponse = await self.sentiment_service.generate_sentiment_rating(
                input_data=input_data,
                model=model
            )
            
            # Create database record
            create_data = SentimentRatingCreate(
                user_id=input_data.user_id,
                summary=input_data.summary,
                mood=input_data.mood,
                energy_level=input_data.energy_level,
                complexity=input_data.complexity,
                satisfaction=input_data.satisfaction,
                sentiment_rating=ai_response.sentiment_rating
            )
            
            # Save to database
            db_record = self.create(create_data.dict())
            
            logger.info(f"Created sentiment rating record {db_record.id} for user {input_data.user_id}")
            
            return SentimentRatingOutput.from_orm(db_record)
            
        except Exception as e:
            logger.error(f"Failed to analyze and create sentiment rating: {e}")
            raise Exception(f"Sentiment analysis failed: {str(e)}")
    
    async def analyze_sentiment_only(
        self, 
        input_data: SentimentRatingInput,
        model: str = "gemini-1.5-pro"
    ) -> SentimentRatingAIResponse:
        """
        Analyze sentiment using AI without saving to database.
        
        Args:
            input_data: The input data for sentiment analysis
            model: AI model to use for analysis
            
        Returns:
            SentimentRatingAIResponse with the AI analysis result
        """
        try:
            return await self.sentiment_service.generate_sentiment_rating(
                input_data=input_data,
                model=model
            )
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            raise Exception(f"Sentiment analysis failed: {str(e)}")
    
    async def batch_analyze_and_create(
        self,
        input_data_list: List[SentimentRatingInput],
        model: str = "gemini-1.5-pro"
    ) -> List[SentimentRatingOutput]:
        """
        Batch analyze sentiments and create database records.
        
        Args:
            input_data_list: List of input data for batch processing
            model: AI model to use for analysis
            
        Returns:
            List of SentimentRatingOutput objects
        """
        results = []
        
        for input_data in input_data_list:
            try:
                result = await self.analyze_and_create_sentiment_rating(
                    input_data=input_data,
                    model=model
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process sentiment for user {input_data.user_id}: {e}")
                # Continue processing other items
                continue
        
        return results
    
    def get_user_sentiment_ratings(
        self, 
        user_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[SentimentRatingOutput]:
        """
        Get sentiment ratings for a specific user.
        
        Args:
            user_id: The user ID to filter by
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of SentimentRatingOutput objects
        """
        try:
            records = (
                self.db.query(SentimentRating)
                .filter(SentimentRating.user_id == user_id)
                .filter(SentimentRating.deleted_at.is_(None))
                .order_by(SentimentRating.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
            
            return [SentimentRatingOutput.from_orm(record) for record in records]
            
        except Exception as e:
            logger.error(f"Failed to get sentiment ratings for user {user_id}: {e}")
            raise Exception(f"Failed to retrieve sentiment ratings: {str(e)}")
    
    def get_sentiment_rating_by_id(self, rating_id: int) -> Optional[SentimentRatingOutput]:
        """
        Get a specific sentiment rating by ID.
        
        Args:
            rating_id: The sentiment rating ID
            
        Returns:
            SentimentRatingOutput if found, None otherwise
        """
        try:
            record = self.get_by_id(rating_id)
            return SentimentRatingOutput.from_orm(record) if record else None
        except Exception as e:
            logger.error(f"Failed to get sentiment rating {rating_id}: {e}")
            return None
    
    def get_sentiment_statistics(self, user_id: int) -> dict:
        """
        Get sentiment statistics for a user.
        
        Args:
            user_id: The user ID to get statistics for
            
        Returns:
            Dictionary with sentiment statistics
        """
        try:
            from sqlalchemy import func
            
            stats = (
                self.db.query(
                    func.count(SentimentRating.id).label('total_count'),
                    func.avg(SentimentRating.sentiment_rating).label('average_rating'),
                    func.min(SentimentRating.sentiment_rating).label('min_rating'),
                    func.max(SentimentRating.sentiment_rating).label('max_rating')
                )
                .filter(SentimentRating.user_id == user_id)
                .filter(SentimentRating.deleted_at.is_(None))
                .first()
            )
            
            return {
                'total_count': stats.total_count or 0,
                'average_rating': float(stats.average_rating or 0),
                'min_rating': float(stats.min_rating or 0),
                'max_rating': float(stats.max_rating or 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get sentiment statistics for user {user_id}: {e}")
            return {
                'total_count': 0,
                'average_rating': 0.0,
                'min_rating': 0.0,
                'max_rating': 0.0
            }
    
    def delete_sentiment_rating(self, rating_id: int) -> bool:
        """
        Soft delete a sentiment rating.
        
        Args:
            rating_id: The sentiment rating ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.soft_delete(rating_id)
        except Exception as e:
            logger.error(f"Failed to delete sentiment rating {rating_id}: {e}")
            return False
    
    def is_service_available(self) -> bool:
        """Check if the sentiment rating service is available."""
        return self.sentiment_service.is_available() 