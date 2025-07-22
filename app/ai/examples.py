"""
Usage examples for the enhanced AI Service with LangChain improvements.
"""
from app.ai import ai_generate, ai_text, ai_json, ai_stream, get_ai_service


async def example_simple_text():
    """Example: Simple text generation with model selection."""
    
    # Method 1: Using convenience function with different models
    haiku = await ai_text(
        prompt="Write a haiku about Python programming",
        system_prompt="You are a creative poet",
        model="gemini-1.5-pro"
    )
    print("Haiku (Pro):", haiku)
    
    # Using faster model for simple tasks
    quick_response = await ai_text(
        prompt="What is machine learning?",
        system_prompt="You are a helpful teacher. Be concise.",
        model="gemini-1.5-flash"
    )
    print("Quick explanation (Flash):", quick_response)
    
    # Method 2: Using the service directly
    ai_service = get_ai_service()
    available_models = ai_service.get_available_models()
    print("Available models:", available_models)


async def example_enhanced_structured_output():
    """Example: Enhanced structured JSON output with better parsing."""
    
    # Complex sentiment analysis
    sentiment_result = await ai_json(
        prompt="Analyze the sentiment of this review: 'The product is amazing but the delivery was delayed and customer service was unhelpful.'",
        schema={
            "overall_sentiment": "string",
            "confidence": "number",
            "aspects": "array",
            "positive_points": "array",
            "negative_points": "array",
            "recommendation": "string"
        },
        system_prompt="You are an expert sentiment analyzer. Provide detailed analysis of different aspects.",
        model="gemini-1.5-pro"
    )
    print("Enhanced Sentiment Analysis:", sentiment_result)
    
    # Information extraction
    extraction_result = await ai_json(
        prompt="Extract information from: 'Dr. Sarah Johnson, a 35-year-old cardiologist from Boston Medical Center, published a research paper on heart disease prevention in March 2024.'",
        schema={
            "name": "string",
            "title": "string",
            "age": "number",
            "profession": "string",
            "organization": "string",
            "location": "string",
            "publication_date": "string",
            "research_topic": "string"
        },
        system_prompt="Extract all relevant information accurately",
        model="gemini-1.5-flash"  # Use faster model for extraction
    )
    print("Information Extraction:", extraction_result)


async def example_streaming_response():
    """Example: Streaming AI responses for real-time applications."""
    
    print("Streaming story generation:")
    print("-" * 50)
    
    async for chunk in ai_stream(
        prompt="Write a short story about a robot learning to paint",
        system_prompt="You are a creative storyteller. Write engagingly."
    ):
        print(chunk, end="", flush=True)
    
    print("\n" + "-" * 50)


async def example_advanced_configurations():
    """Example: Advanced configurations with different models and parameters."""
    
    # Creative writing with high temperature
    creative_story = await ai_generate(
        user_prompt="Write a surreal short story about time travel",
        system_prompt="You are a creative writer specializing in surreal fiction",
        model="gemini-1.5-pro",
        temperature=1.2,  # Higher creativity
        max_tokens=800
    )
    print("Creative Story:", creative_story)
    
    # Factual response with low temperature
    technical_explanation = await ai_generate(
        user_prompt="Explain how quantum computers work",
        system_prompt="You are a technical expert. Be precise and factual.",
        model="gemini-1.5-pro",
        temperature=0.1,  # Lower creativity, more factual
        max_tokens=500
    )
    print("Technical Explanation:", technical_explanation)
    
    # Fast response for simple queries
    quick_answer = await ai_generate(
        user_prompt="What's the capital of France?",
        model="gemini-1.5-flash",  # Fastest model
        temperature=0.0,
        max_tokens=50
    )
    print("Quick Answer:", quick_answer)


async def example_enhanced_endpoint_usage():
    """Example: Enhanced usage in endpoints with error handling."""
    
    # Simulate user feedback analysis with comprehensive output
    feedback = "The app is fantastic and the UI is beautiful, but it crashes sometimes and the loading is slow"
    
    try:
        feedback_analysis = await ai_json(
            prompt=f"Analyze this user feedback comprehensively: '{feedback}'",
            schema={
                "overall_sentiment": "string",
                "sentiment_score": "number",
                "key_strengths": "array",
                "key_issues": "array",
                "severity_level": "string",
                "suggested_actions": "array",
                "user_satisfaction": "number",
                "categories": "array"
            },
            system_prompt="""You are a product manager analyzing user feedback. 
            Provide comprehensive analysis including sentiment, specific issues, 
            and actionable recommendations. Rate severity as low/medium/high.""",
            model="gemini-1.5-pro"
        )
        
        print("Comprehensive Feedback Analysis:", feedback_analysis)
        
    except Exception as e:
        print(f"Error analyzing feedback: {e}")
        # Fallback to simpler analysis
        simple_analysis = await ai_text(
            f"Briefly analyze this feedback: '{feedback}'",
            "Provide a short summary of the main points",
            model="gemini-1.5-flash"
        )
        print("Fallback Analysis:", simple_analysis)


async def example_content_generation_pipeline():
    """Example: Multi-step content generation pipeline."""
    
    topic = "sustainable energy solutions"
    
    # Step 1: Generate outline
    outline = await ai_json(
        prompt=f"Create a detailed outline for an article about {topic}",
        schema={
            "title": "string",
            "introduction": "string",
            "main_sections": "array",
            "conclusion": "string",
            "target_audience": "string",
            "estimated_length": "string"
        },
        system_prompt="You are a content strategist creating article outlines",
        model="gemini-1.5-pro"
    )
    print("Article Outline:", outline)
    
    # Step 2: Generate introduction based on outline
    introduction = await ai_text(
        prompt=f"Write an engaging introduction for an article titled '{outline['title']}' targeting {outline['target_audience']}",
        system_prompt="You are a skilled technical writer",
        model="gemini-1.5-pro",
        temperature=0.8
    )
    print("Generated Introduction:", introduction)


async def example_safety_and_moderation():
    """Example: Content safety and moderation using AI."""
    
    test_contents = [
        "This is a great product review!",
        "I love using this application daily",
        "The customer service was helpful and friendly"
    ]
    
    for content in test_contents:
        safety_check = await ai_json(
            prompt=f"Analyze this content for safety and appropriateness: '{content}'",
            schema={
                "is_safe": "boolean",
                "confidence": "number",
                "concerns": "array",
                "severity": "string",
                "recommended_action": "string"
            },
            system_prompt="""You are a content moderation expert. 
            Analyze content for harmful, inappropriate, or unsafe material. 
            Rate severity as none/low/medium/high.""",
            model="gemini-1.5-pro",
            temperature=0.2  # Low temperature for consistent moderation
        )
        print(f"Safety check for '{content}': {safety_check}")


# Example of using enhanced AI in your existing endpoints
"""
Enhanced endpoint examples with new features:

from app.ai import ai_text, ai_json, ai_stream
from fastapi.responses import StreamingResponse

@router.post("/analyze-feedback-advanced")
async def analyze_feedback_advanced(feedback: str, analysis_type: str = "comprehensive"):
    if analysis_type == "comprehensive":
        return await ai_json(
            f"Analyze this feedback comprehensively: '{feedback}'",
            {
                "sentiment": "string",
                "issues": "array", 
                "suggestions": "array",
                "priority": "string",
                "satisfaction_score": "number"
            },
            "You are a product analyst",
            model="gemini-1.5-pro"
        )
    else:
        return await ai_text(
            f"Briefly analyze: '{feedback}'",
            "Provide a quick summary",
            model="gemini-1.5-flash"
        )

@router.get("/welcome/{username}")
async def welcome_user_personalized(username: str, style: str = "friendly"):
    system_prompts = {
        "friendly": "You are a warm, friendly assistant",
        "professional": "You are a professional customer service representative", 
        "casual": "You are a casual, fun assistant"
    }
    
    message = await ai_text(
        f"Create a {style} welcome message for {username}",
        system_prompts.get(style, system_prompts["friendly"]),
        model="gemini-1.5-flash"
    )
    return {"message": message}

@router.get("/generate-content-stream")
async def stream_content(topic: str):
    async def generate():
        async for chunk in ai_stream(
            f"Write an article about {topic}",
            "You are a technical writer"
        ):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

@router.post("/moderate-content")
async def moderate_content(content: str):
    return await ai_json(
        f"Check if this content is appropriate: '{content}'",
        {
            "is_safe": "boolean",
            "concerns": "array",
            "confidence": "number"
        },
        "You are a content moderator",
        model="gemini-1.5-pro",
        temperature=0.1  # Very consistent for moderation
    )
""" 