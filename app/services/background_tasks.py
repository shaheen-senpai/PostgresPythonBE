"""
Background task functions for async processing.
"""
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.vibe_log import VibeLog, MoodEnum, ComplexityEnum
from app.ai.sentiment_rating_service import get_sentiment_rating_service
from app.schemas.sentiment_rating import SentimentRatingInput

logger = logging.getLogger(__name__)


async def process_vibe_log_sentiment(vibe_log_id: int, vibe_log_data: Dict[str, Any]):
    """
    Background task to process sentiment analysis for a vibe log using AI service.
    
    Args:
        vibe_log_id: ID of the vibe log to update
        vibe_log_data: Vibe log data for sentiment analysis
    """
    try:
        logger.info(f"Starting AI sentiment analysis for vibe_log_id: {vibe_log_id}")
        
        # Get sentiment service
        sentiment_service = get_sentiment_rating_service()
        
        # Check if service is available
        if not sentiment_service.is_available():
            logger.warning(f"AI sentiment service not available for vibe_log_id: {vibe_log_id}")
            return
        
        # Create sentiment rating input
        sentiment_input = SentimentRatingInput(
            user_id=vibe_log_data["user_id"],
            summary=vibe_log_data["summary"],
            mood=MoodEnum(vibe_log_data["mood"]),
            energy_level=vibe_log_data["energy_level"],
            complexity=ComplexityEnum(vibe_log_data["complexity"]),
            satisfaction=vibe_log_data["satisfaction"]
        )
        
        # Analyze sentiment using AI
        sentiment_response = await sentiment_service.generate_sentiment_rating(sentiment_input)
        
        if sentiment_response and sentiment_response.sentiment_rating is not None:
            # Update vibe log with sentiment score directly using SQLAlchemy
            db: Session = next(get_db())
            try:
                vibe_log = db.query(VibeLog).filter(VibeLog.id == vibe_log_id).first()
                if vibe_log:
                    # Update the sentiment_rating field
                    vibe_log.sentiment_rating = sentiment_response.sentiment_rating
                    db.commit()
                    db.refresh(vibe_log)
                    logger.info(f"Updated vibe_log {vibe_log_id} with AI sentiment score: {sentiment_response.sentiment_rating}")
                else:
                    logger.error(f"Vibe log {vibe_log_id} not found for sentiment update")
            except Exception as db_error:
                logger.error(f"Database error updating vibe_log {vibe_log_id}: {str(db_error)}")
                db.rollback()
            finally:
                db.close()
        else:
            logger.warning(f"Failed to get AI sentiment score for vibe_log_id: {vibe_log_id}")
            
    except Exception as e:
        logger.error(f"Error processing AI sentiment for vibe_log_id {vibe_log_id}: {str(e)}")


def create_vibe_log_data_dict(vibe_log_obj) -> Dict[str, Any]:
    """
    Convert vibe log object to dictionary for sentiment analysis.
    
    Args:
        vibe_log_obj: VibeLog SQLAlchemy object
        
    Returns:
        Dictionary with vibe log data
    """
    return {
        "user_id": vibe_log_obj.user_id,
        "summary": vibe_log_obj.summary,
        "mood": vibe_log_obj.mood.value if hasattr(vibe_log_obj.mood, 'value') else str(vibe_log_obj.mood),
        "energy_level": vibe_log_obj.energy_level,
        "complexity": vibe_log_obj.complexity.value if hasattr(vibe_log_obj.complexity, 'value') else str(vibe_log_obj.complexity),
        "satisfaction": vibe_log_obj.satisfaction
    }