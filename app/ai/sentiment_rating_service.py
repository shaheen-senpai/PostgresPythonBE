"""
Sentiment Rating Service that uses AI to analyze user mood and generate sentiment ratings.
"""
from typing import Optional
from langchain_core.pydantic_v1 import BaseModel as PydanticBaseModel, Field

from app.ai.ai_service import get_ai_service
from app.schemas.sentiment_rating import SentimentRatingInput, SentimentRatingAIResponse
from app.utils.logger import logger


class SentimentAnalysisResponse(PydanticBaseModel):
    """Pydantic model for AI sentiment analysis response."""
    user_id: int = Field(..., description="User ID from the input")
    sentiment_rating: float = Field(..., description="Sentiment rating out of 100 based on mood, energy, complexity and satisfaction analysis")


class SentimentRatingService:
    """
    Service for generating sentiment ratings using AI analysis.
    
    This service takes user mood data and uses the Gemini AI to generate
    a comprehensive sentiment rating out of 100.
    """
    
    def __init__(self):
        self.ai_service = get_ai_service()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for sentiment analysis."""
        return """You are an expert psychologist and sentiment analyst specializing in mood assessment and emotional intelligence.

Your task is to analyze user mood data and generate a comprehensive sentiment rating out of 100.

Consider these factors in your analysis:
1. **Mood**: The user's emotional state (sad, angry, happy, good, excited)
2. **Energy Level**: Physical and mental energy on a 1-5 scale
3. **Complexity**: How challenging their current situation is (easy, medium, hard, very_hard)
4. **Satisfaction**: Their satisfaction level on a 1-10 scale
5. **Summary**: Context about their current situation

**Rating Scale Guidelines:**
- 0-20: Very negative sentiment (sad/angry mood, low energy, high complexity, low satisfaction)
- 21-40: Negative sentiment (mixed negative factors)
- 41-60: Neutral sentiment (balanced or conflicting factors)
- 61-80: Positive sentiment (generally positive factors)
- 81-100: Very positive sentiment (happy/excited mood, high energy, manageable complexity, high satisfaction)

**Analysis Approach:**
- Weight satisfaction and mood most heavily (40% each)
- Energy level contributes 15%
- Complexity contributes 5% (inverse relationship - higher complexity lowers sentiment)
- Use the summary to provide context and fine-tune the rating

Be precise and consistent in your analysis. The rating should reflect the overall emotional and psychological state of the user."""
    
    def _create_user_prompt(self, input_data: SentimentRatingInput) -> str:
        """Create the user prompt with the input data."""
        return f"""Please analyze the following user data and provide a sentiment rating:

**User ID:** {input_data.user_id}
**Summary:** "{input_data.summary}"
**Current Mood:** {input_data.mood.value}
**Energy Level:** {input_data.energy_level}/5
**Situation Complexity:** {input_data.complexity.value}
**Satisfaction Level:** {input_data.satisfaction}/10

Based on this information, generate a comprehensive sentiment rating out of 100 that reflects the user's overall emotional and psychological state."""
    
    async def generate_sentiment_rating(
        self, 
        input_data: SentimentRatingInput,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.3
    ) -> SentimentRatingAIResponse:
        """
        Generate sentiment rating using AI analysis.
        
        Args:
            input_data: The input data containing user mood information
            model: AI model to use (default: gemini-1.5-pro)
            temperature: Temperature for AI generation (default: 0.3 for consistency)
        
        Returns:
            SentimentRatingAIResponse with the generated sentiment rating
        
        Raises:
            Exception: If AI service is not available or analysis fails
        """
        try:
            logger.info(f"Generating sentiment rating for user {input_data.user_id}")
            
            # Create prompts
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(input_data)
            
            # Generate structured response using AI service
            ai_response = await self.ai_service.generate_structured(
                user_prompt=user_prompt,
                output_model=SentimentAnalysisResponse,
                system_prompt=system_prompt,
                model=model,
                temperature=temperature
            )
            
            # Convert to our response schema
            response = SentimentRatingAIResponse(
                user_id=ai_response.user_id,
                sentiment_rating=ai_response.sentiment_rating
            )
            
            logger.info(f"Generated sentiment rating {response.sentiment_rating} for user {input_data.user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate sentiment rating for user {input_data.user_id}: {e}")
            raise Exception(f"Sentiment rating generation failed: {str(e)}")
    
    async def analyze_sentiment_batch(
        self,
        input_data_list: list[SentimentRatingInput],
        model: str = "gemini-2.0-flash",
        temperature: float = 0.3
    ) -> list[SentimentRatingAIResponse]:
        """
        Generate sentiment ratings for multiple inputs.
        
        Args:
            input_data_list: List of input data for batch processing
            model: AI model to use
            temperature: Temperature for AI generation
        
        Returns:
            List of SentimentRatingAIResponse objects
        """
        results = []
        for input_data in input_data_list:
            try:
                result = await self.generate_sentiment_rating(
                    input_data=input_data,
                    model=model,
                    temperature=temperature
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process sentiment rating for user {input_data.user_id}: {e}")
                # You might want to handle this differently based on your requirements
                continue
        
        return results
    
    def is_available(self) -> bool:
        """Check if the sentiment rating service is available."""
        return self.ai_service.is_available()


# Global instance
_sentiment_rating_service_instance: Optional[SentimentRatingService] = None


def get_sentiment_rating_service() -> SentimentRatingService:
    """
    Get global sentiment rating service instance.
    
    Returns:
        SentimentRatingService instance
    """
    global _sentiment_rating_service_instance
    if _sentiment_rating_service_instance is None:
        _sentiment_rating_service_instance = SentimentRatingService()
    return _sentiment_rating_service_instance


# Convenience function for quick sentiment rating
async def generate_sentiment_rating(
    input_data: SentimentRatingInput,
    model: str = "gemini-2.0-flash",
    temperature: float = 0.3
) -> SentimentRatingAIResponse:
    """
    Quick sentiment rating generation function.
    
    Usage:
        from app.schemas.sentiment_rating import SentimentRatingInput
        from app.models.sentiment_rating import MoodEnum, ComplexityEnum
        from app.ai.sentiment_rating_service import generate_sentiment_rating
        
        input_data = SentimentRatingInput(
            user_id=1,
            summary="Had a great day at work, completed all tasks",
            mood=MoodEnum.HAPPY,
            energy_level=4,
            complexity=ComplexityEnum.EASY,
            satisfaction=8.5
        )
        
        result = await generate_sentiment_rating(input_data)
        print(f"Sentiment rating: {result.sentiment_rating}")
    """
    service = get_sentiment_rating_service()
    return await service.generate_sentiment_rating(
        input_data=input_data,
        model=model,
        temperature=temperature
    ) 