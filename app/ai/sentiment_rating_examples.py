"""
Examples and usage patterns for the Sentiment Rating Service.
"""
import asyncio
from app.ai.sentiment_rating_service import generate_sentiment_rating, get_sentiment_rating_service
from app.schemas.sentiment_rating import SentimentRatingInput
from app.models.sentiment_rating import MoodEnum, ComplexityEnum


async def example_positive_sentiment():
    """Example: High positive sentiment rating."""
    
    input_data = SentimentRatingInput(
        user_id=1,
        summary="Had an amazing day at work! Completed a major project and received praise from my manager.",
        mood=MoodEnum.EXCITED,
        energy_level=5,
        complexity=ComplexityEnum.EASY,
        satisfaction=9.5
    )
    
    result = await generate_sentiment_rating(input_data)
    print(f"Positive Example - Sentiment Rating: {result.sentiment_rating}/100")
    return result


async def example_negative_sentiment():
    """Example: Low negative sentiment rating."""
    
    input_data = SentimentRatingInput(
        user_id=2,
        summary="Struggling with multiple deadlines and feeling overwhelmed by work pressure.",
        mood=MoodEnum.SAD,
        energy_level=2,
        complexity=ComplexityEnum.VERY_HARD,
        satisfaction=3.0
    )
    
    result = await generate_sentiment_rating(input_data)
    print(f"Negative Example - Sentiment Rating: {result.sentiment_rating}/100")
    return result


async def example_neutral_sentiment():
    """Example: Neutral sentiment rating."""
    
    input_data = SentimentRatingInput(
        user_id=3,
        summary="Regular day at the office, nothing special happened but got my tasks done.",
        mood=MoodEnum.GOOD,
        energy_level=3,
        complexity=ComplexityEnum.MEDIUM,
        satisfaction=6.5
    )
    
    result = await generate_sentiment_rating(input_data)
    print(f"Neutral Example - Sentiment Rating: {result.sentiment_rating}/100")
    return result


async def example_mixed_sentiment():
    """Example: Mixed sentiment with conflicting factors."""
    
    input_data = SentimentRatingInput(
        user_id=4,
        summary="Great personal achievement but dealing with some family stress at home.",
        mood=MoodEnum.HAPPY,
        energy_level=4,
        complexity=ComplexityEnum.HARD,
        satisfaction=7.0
    )
    
    result = await generate_sentiment_rating(input_data)
    print(f"Mixed Example - Sentiment Rating: {result.sentiment_rating}/100")
    return result


async def example_angry_sentiment():
    """Example: Angry mood with high complexity."""
    
    input_data = SentimentRatingInput(
        user_id=5,
        summary="Frustrated with technical issues that are blocking my progress on important work.",
        mood=MoodEnum.ANGRY,
        energy_level=3,
        complexity=ComplexityEnum.VERY_HARD,
        satisfaction=2.5
    )
    
    result = await generate_sentiment_rating(input_data)
    print(f"Angry Example - Sentiment Rating: {result.sentiment_rating}/100")
    return result


async def example_batch_processing():
    """Example: Batch processing multiple sentiment ratings."""
    
    input_data_list = [
        SentimentRatingInput(
            user_id=6,
            summary="Excited about starting a new hobby - learning guitar!",
            mood=MoodEnum.EXCITED,
            energy_level=4,
            complexity=ComplexityEnum.MEDIUM,
            satisfaction=8.0
        ),
        SentimentRatingInput(
            user_id=7,
            summary="Feeling tired after a long week but satisfied with accomplishments.",
            mood=MoodEnum.GOOD,
            energy_level=2,
            complexity=ComplexityEnum.EASY,
            satisfaction=7.5
        ),
        SentimentRatingInput(
            user_id=8,
            summary="Dealing with a difficult client situation that's causing stress.",
            mood=MoodEnum.ANGRY,
            energy_level=3,
            complexity=ComplexityEnum.HARD,
            satisfaction=4.0
        )
    ]
    
    service = get_sentiment_rating_service()
    results = await service.analyze_sentiment_batch(input_data_list)
    
    print("Batch Processing Results:")
    for result in results:
        print(f"  User {result.user_id}: {result.sentiment_rating}/100")
    
    return results


async def example_different_models():
    """Example: Using different AI models for sentiment analysis."""
    
    input_data = SentimentRatingInput(
        user_id=9,
        summary="Moderate day with some ups and downs, overall feeling okay.",
        mood=MoodEnum.GOOD,
        energy_level=3,
        complexity=ComplexityEnum.MEDIUM,
        satisfaction=6.0
    )
    
    # Using different models
    models = ["gemini-1.5-pro", "gemini-1.5-flash"]
    
    for model in models:
        result = await generate_sentiment_rating(input_data, model=model)
        print(f"Model {model} - Sentiment Rating: {result.sentiment_rating}/100")


async def example_temperature_variations():
    """Example: Using different temperature settings for consistency vs creativity."""
    
    input_data = SentimentRatingInput(
        user_id=10,
        summary="Complex situation with both positive and negative aspects to consider.",
        mood=MoodEnum.GOOD,
        energy_level=3,
        complexity=ComplexityEnum.HARD,
        satisfaction=6.5
    )
    
    temperatures = [0.1, 0.3, 0.7]  # Low to high creativity
    
    for temp in temperatures:
        result = await generate_sentiment_rating(input_data, temperature=temp)
        print(f"Temperature {temp} - Sentiment Rating: {result.sentiment_rating}/100")


# Sample System and User Prompts for Documentation
SAMPLE_SYSTEM_PROMPT = """You are an expert psychologist and sentiment analyst specializing in mood assessment and emotional intelligence.

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

SAMPLE_USER_PROMPT = """Please analyze the following user data and provide a sentiment rating:

**User ID:** 1
**Summary:** "Had an amazing day at work! Completed a major project and received praise from my manager."
**Current Mood:** excited
**Energy Level:** 5/5
**Situation Complexity:** easy
**Satisfaction Level:** 9.5/10

Based on this information, generate a comprehensive sentiment rating out of 100 that reflects the user's overall emotional and psychological state."""

# Expected response schema documentation
SAMPLE_RESPONSE_SCHEMA = {
    "user_id": "int - The user ID from the input",
    "sentiment_rating": "float - Sentiment rating out of 100 based on comprehensive mood analysis"
}


async def run_all_examples():
    """Run all sentiment rating examples."""
    print("=== Sentiment Rating Service Examples ===\n")
    
    print("1. Positive Sentiment Example:")
    await example_positive_sentiment()
    
    print("\n2. Negative Sentiment Example:")
    await example_negative_sentiment()
    
    print("\n3. Neutral Sentiment Example:")
    await example_neutral_sentiment()
    
    print("\n4. Mixed Sentiment Example:")
    await example_mixed_sentiment()
    
    print("\n5. Angry Sentiment Example:")
    await example_angry_sentiment()
    
    print("\n6. Batch Processing Example:")
    await example_batch_processing()
    
    print("\n7. Different Models Example:")
    await example_different_models()
    
    print("\n8. Temperature Variations Example:")
    await example_temperature_variations()
    
    print("\n=== Sample Prompts for Documentation ===")
    print("\nSystem Prompt:")
    print(SAMPLE_SYSTEM_PROMPT)
    
    print("\nUser Prompt:")
    print(SAMPLE_USER_PROMPT)
    
    print("\nResponse Schema:")
    print(SAMPLE_RESPONSE_SCHEMA)


if __name__ == "__main__":
    asyncio.run(run_all_examples()) 