# Sentiment Rating Service

A comprehensive AI-powered sentiment analysis service that analyzes user mood data and generates sentiment ratings using Google's Gemini AI.

## Overview

The Sentiment Rating Service takes user mood data including summary, mood, energy level, complexity, and satisfaction, then uses AI to generate a comprehensive sentiment rating out of 100.

## Architecture

- **AI Service**: Uses the existing `AIService` with structured output
- **Database Model**: `SentimentRating` model with indexed fields
- **Schemas**: Pydantic models for input/output validation
- **Controller**: Business logic for CRUD operations
- **Service Integration**: Designed to be called from existing endpoints

## Database Schema

### Input Fields

- `user_id`: Foreign key indexed (INTEGER)
- `summary`: VARCHAR(100) - Context about the user's situation
- `mood`: ENUM (sad, angry, happy, good, excited)
- `energy_level`: INTEGER (1–5 scale)
- `complexity`: ENUM (easy, medium, hard, very_hard)
- `satisfaction`: FLOAT (1–10 scale)

### Output Fields

- `id`: Primary key (INTEGER)
- `sentiment_rating`: FLOAT (out of 100) - AI generated
- Standard base fields: `created_at`, `updated_at`, `deleted_at`

## AI Response Schema

```json
{
  "user_id": "int - User ID from input",
  "sentiment_rating": "float - Sentiment rating out of 100"
}
```

## System Prompt

```
You are an expert psychologist and sentiment analyst specializing in mood assessment and emotional intelligence.

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

Be precise and consistent in your analysis. The rating should reflect the overall emotional and psychological state of the user.
```

## Sample User Prompt

```
Please analyze the following user data and provide a sentiment rating:

**User ID:** 1
**Summary:** "Had an amazing day at work! Completed a major project and received praise from my manager."
**Current Mood:** excited
**Energy Level:** 5/5
**Situation Complexity:** easy
**Satisfaction Level:** 9.5/10

Based on this information, generate a comprehensive sentiment rating out of 100 that reflects the user's overall emotional and psychological state.
```

## Usage Examples

### 1. Direct Service Usage

```python
from app.ai.sentiment_rating_service import generate_sentiment_rating
from app.schemas.sentiment_rating import SentimentRatingInput
from app.models.sentiment_rating import MoodEnum, ComplexityEnum

# Create input data
input_data = SentimentRatingInput(
    user_id=1,
    summary="Had a great day at work, completed all tasks",
    mood=MoodEnum.HAPPY,
    energy_level=4,
    complexity=ComplexityEnum.EASY,
    satisfaction=8.5
)

# Generate sentiment rating
result = await generate_sentiment_rating(input_data)
print(f"Sentiment rating: {result.sentiment_rating}")
```

### 2. Using the Controller

```python
from app.controllers.sentiment_rating_controller import SentimentRatingController
from app.config.database import get_db

# Get database session
db = next(get_db())

# Create controller
controller = SentimentRatingController(db)

# Analyze and save to database
result = await controller.analyze_and_create_sentiment_rating(input_data)
print(f"Created record with ID: {result.id}")
```

### 3. Integration in Existing Endpoints

The service is designed to be used within your existing API endpoints. Here's how to integrate it:

## Service Integration

To use this service in other endpoints:

```python
from app.ai.sentiment_rating_service import generate_sentiment_rating

@router.post("/my-endpoint")
async def my_endpoint(data: MyData):
    # Create sentiment input from your data
    sentiment_input = SentimentRatingInput(
        user_id=data.user_id,
        summary=data.description,
        mood=data.mood,
        energy_level=data.energy,
        complexity=data.difficulty,
        satisfaction=data.satisfaction_score
    )

    # Get sentiment rating
    sentiment_result = await generate_sentiment_rating(sentiment_input)

    # Use the rating in your business logic
    return {
        "sentiment_rating": sentiment_result.sentiment_rating,
        "analysis_result": "Your custom logic here"
    }
```

## Available Models

- `gemini-1.5-pro` (default) - Best accuracy
- `gemini-1.5-flash` - Faster processing

## Error Handling

The service includes comprehensive error handling:

- AI service availability checks
- Input validation with Pydantic
- Database operation error handling
- Detailed logging for debugging

## Testing

Run the examples to test the service:

```python
from app.ai.sentiment_rating_examples import run_all_examples
import asyncio

asyncio.run(run_all_examples())
```

## Configuration

Ensure your environment has:

- `GOOGLE_API_KEY` set for Gemini AI access
- Database connection configured
- All dependencies installed

## Performance Considerations

- Use `gemini-1.5-flash` for faster processing when accuracy is less critical
- Batch processing available for multiple analyses
- Database indexes optimize query performance
- Soft delete maintains data integrity

## Monitoring

Check service health programmatically:

```python
from app.ai.sentiment_rating_service import get_sentiment_rating_service

service = get_sentiment_rating_service()
is_available = service.is_available()
```

Or using the controller:

```python
from app.controllers.sentiment_rating_controller import SentimentRatingController

controller = SentimentRatingController(db)
is_available = controller.is_service_available()
```
