"""
Comprehensive examples for structured AI output using Pydantic models.
Based on LangChain's recommended approach with with_structured_output().
"""
from typing import List, Optional
from langchain_core.pydantic_v1 import BaseModel, Field

from app.ai import ai_structured, ai_sentiment, ai_extract_person, ai_moderate_content, ai_analyze_feedback


# Example 1: Basic Person Information (from LangChain docs)
class Person(BaseModel):
    """Information about a person."""
    name: str = Field(..., description="The person's name")
    height_m: Optional[float] = Field(None, description="The person's height in meters")
    age: Optional[int] = Field(None, description="The person's age in years")


async def example_basic_person_extraction():
    """Example: Basic person information extraction like in LangChain docs."""
    
    result = await ai_structured(
        "Who was the 16th president of the USA, and how tall was he in meters?",
        Person,
        system_prompt="Extract person information accurately",
        model="gemini-1.5-pro",
        temperature=0  # Low temperature for factual accuracy
    )
    
    print(f"Name: {result.name}")
    print(f"Height: {result.height_m}m")
    print(f"Age: {result.age}")
    return result


# Example 2: Complex Sentiment Analysis
class DetailedSentimentAnalysis(BaseModel):
    """Detailed sentiment analysis with multiple aspects."""
    overall_sentiment: str = Field(..., description="Overall sentiment: positive, negative, or neutral")
    confidence: float = Field(..., description="Confidence score between 0 and 1")
    emotional_tone: str = Field(..., description="Emotional tone: happy, sad, angry, excited, etc.")
    subjectivity: str = Field(..., description="Subjectivity: objective or subjective")
    keywords: List[str] = Field(..., description="Key words that influenced the sentiment")
    aspects: List[dict] = Field(..., description="Sentiment for different aspects mentioned")


async def example_detailed_sentiment():
    """Example: Detailed sentiment analysis with multiple aspects."""
    
    text = "I absolutely love the design of this product! It's beautiful and intuitive. However, the customer service was terrible and the shipping took forever. Overall, I'm satisfied but there's room for improvement."
    
    result = await ai_structured(
        f"Perform detailed sentiment analysis on: '{text}'",
        DetailedSentimentAnalysis,
        "You are an expert sentiment analyzer. Analyze all aspects of the text including overall sentiment, emotional tone, and specific aspects mentioned.",
        model="gemini-1.5-pro"
    )
    
    print(f"Overall Sentiment: {result.overall_sentiment}")
    print(f"Confidence: {result.confidence}")
    print(f"Emotional Tone: {result.emotional_tone}")
    print(f"Keywords: {result.keywords}")
    print(f"Aspects: {result.aspects}")
    return result


# Example 3: Product Information Extraction
class ProductInfo(BaseModel):
    """Product information extraction."""
    name: str = Field(..., description="Product name")
    brand: Optional[str] = Field(None, description="Brand name")
    price: Optional[float] = Field(None, description="Price in USD")
    category: Optional[str] = Field(None, description="Product category")
    features: List[str] = Field(default=[], description="Key features mentioned")
    availability: Optional[str] = Field(None, description="Availability status")
    rating: Optional[float] = Field(None, description="Rating out of 5 stars")


async def example_product_extraction():
    """Example: Extract product information from text."""
    
    text = "The iPhone 15 Pro by Apple costs $999 and is available now. It features a titanium design, A17 Pro chip, and improved cameras. Rated 4.5 stars by users."
    
    result = await ai_structured(
        f"Extract product information from: '{text}'",
        ProductInfo,
        "Extract all available product information accurately",
        model="gemini-1.5-flash"  # Fast model for extraction
    )
    
    print(f"Product: {result.name}")
    print(f"Brand: {result.brand}")
    print(f"Price: ${result.price}")
    print(f"Features: {result.features}")
    print(f"Rating: {result.rating}/5")
    return result


# Example 4: Meeting Summary
class MeetingSummary(BaseModel):
    """Meeting summary with action items."""
    title: str = Field(..., description="Meeting title or topic")
    date: Optional[str] = Field(None, description="Meeting date")
    participants: List[str] = Field(..., description="List of participants")
    key_points: List[str] = Field(..., description="Main discussion points")
    decisions: List[str] = Field(..., description="Decisions made")
    action_items: List[dict] = Field(..., description="Action items with assignee and deadline")
    next_meeting: Optional[str] = Field(None, description="Next meeting date/time")


async def example_meeting_summary():
    """Example: Generate structured meeting summary."""
    
    meeting_text = """
    Yesterday's product planning meeting with Sarah, John, and Mike discussed the Q1 roadmap. 
    We decided to prioritize the mobile app redesign and delay the web dashboard updates. 
    Sarah will create wireframes by Friday, John will research competitors by next week, 
    and Mike will prepare the technical specifications by Monday. 
    Next meeting scheduled for January 15th at 2 PM.
    """
    
    result = await ai_structured(
        f"Create a structured meeting summary from: '{meeting_text}'",
        MeetingSummary,
        "You are an executive assistant creating meeting summaries",
        model="gemini-1.5-pro"
    )
    
    print(f"Meeting: {result.title}")
    print(f"Participants: {result.participants}")
    print(f"Key Points: {result.key_points}")
    print(f"Decisions: {result.decisions}")
    print(f"Action Items: {result.action_items}")
    return result


# Example 5: Code Analysis
class CodeAnalysis(BaseModel):
    """Code analysis and review."""
    language: str = Field(..., description="Programming language")
    complexity: str = Field(..., description="Code complexity: low, medium, high")
    issues: List[str] = Field(default=[], description="Potential issues or bugs")
    suggestions: List[str] = Field(default=[], description="Improvement suggestions")
    security_concerns: List[str] = Field(default=[], description="Security concerns")
    performance_score: int = Field(..., description="Performance score out of 10")
    maintainability_score: int = Field(..., description="Maintainability score out of 10")


async def example_code_analysis():
    """Example: Analyze code structure and quality."""
    
    code = """
    def process_user_data(data):
        result = []
        for item in data:
            if item['age'] > 18:
                result.append(item['name'].upper())
        return result
    """
    
    result = await ai_structured(
        f"Analyze this code for quality, issues, and improvements: {code}",
        CodeAnalysis,
        "You are a senior software engineer reviewing code",
        model="gemini-1.5-pro"
    )
    
    print(f"Language: {result.language}")
    print(f"Complexity: {result.complexity}")
    print(f"Issues: {result.issues}")
    print(f"Suggestions: {result.suggestions}")
    print(f"Performance: {result.performance_score}/10")
    return result


# Example 6: Using Built-in Convenience Functions
async def example_builtin_functions():
    """Example: Using built-in convenience functions."""
    
    # Quick sentiment analysis
    sentiment = await ai_sentiment("I'm really excited about this new feature!")
    print(f"Sentiment: {sentiment.sentiment} (confidence: {sentiment.confidence})")
    
    # Person extraction
    person = await ai_extract_person("Dr. Jane Smith, a 45-year-old cardiologist from Boston")
    print(f"Person: {person.name}, {person.age} years old, {person.profession}")
    
    # Content moderation
    moderation = await ai_moderate_content("This is a great product review!")
    print(f"Safe: {moderation.is_safe}, Confidence: {moderation.confidence}")
    
    # Feedback analysis
    feedback = await ai_analyze_feedback("The app is amazing but crashes sometimes")
    print(f"Sentiment: {feedback.overall_sentiment}")
    print(f"Issues: {feedback.key_issues}")
    print(f"Satisfaction: {feedback.user_satisfaction}/10")


# Example 7: Custom Business Logic Model
class CustomerSupportTicket(BaseModel):
    """Customer support ticket analysis."""
    ticket_id: Optional[str] = Field(None, description="Ticket ID if mentioned")
    customer_name: Optional[str] = Field(None, description="Customer name")
    issue_category: str = Field(..., description="Issue category: technical, billing, account, product")
    priority: str = Field(..., description="Priority level: low, medium, high, urgent")
    sentiment: str = Field(..., description="Customer sentiment: positive, negative, neutral")
    issue_description: str = Field(..., description="Brief description of the issue")
    suggested_resolution: str = Field(..., description="Suggested resolution approach")
    estimated_resolution_time: str = Field(..., description="Estimated time to resolve")
    requires_escalation: bool = Field(..., description="Whether this requires escalation")


async def example_support_ticket():
    """Example: Analyze customer support ticket."""
    
    ticket_text = """
    Hi, I'm John Davis and I'm really frustrated. I've been trying to log into my account for 3 days 
    but keep getting an error message. I'm a premium customer and this is unacceptable. 
    I need this fixed immediately as I have an important presentation tomorrow. 
    My account email is john@company.com. Please help ASAP!
    """
    
    result = await ai_structured(
        f"Analyze this customer support request: '{ticket_text}'",
        CustomerSupportTicket,
        "You are a customer support manager analyzing incoming tickets",
        model="gemini-1.5-pro"
    )
    
    print(f"Customer: {result.customer_name}")
    print(f"Category: {result.issue_category}")
    print(f"Priority: {result.priority}")
    print(f"Sentiment: {result.sentiment}")
    print(f"Issue: {result.issue_description}")
    print(f"Suggested Resolution: {result.suggested_resolution}")
    print(f"Escalation Required: {result.requires_escalation}")
    return result


# Example for use in endpoints
async def example_endpoint_usage():
    """Example: How to use structured output in your endpoints."""
    
    # This is how you would use it in your FastAPI endpoints
    """
    from app.ai import ai_structured
    from app.ai.structured_examples import CustomerSupportTicket, ProductInfo
    
    @router.post("/analyze-support-ticket")
    async def analyze_ticket(ticket_content: str):
        analysis = await ai_structured(
            f"Analyze this support ticket: '{ticket_content}'",
            CustomerSupportTicket,
            "You are a customer support manager",
            model="gemini-1.5-pro"
        )
        
        return {
            "priority": analysis.priority,
            "category": analysis.issue_category,
            "sentiment": analysis.sentiment,
            "escalation_required": analysis.requires_escalation,
            "suggested_resolution": analysis.suggested_resolution
        }
    
    @router.post("/extract-product-info")
    async def extract_product(product_description: str):
        product = await ai_structured(
            f"Extract product information: '{product_description}'",
            ProductInfo,
            "Extract all available product details",
            model="gemini-1.5-flash"
        )
        
        return product.dict()  # Convert to dictionary for JSON response
    """


# Run all examples
async def run_all_examples():
    """Run all structured output examples."""
    print("=== Basic Person Extraction ===")
    await example_basic_person_extraction()
    
    print("\n=== Detailed Sentiment Analysis ===")
    await example_detailed_sentiment()
    
    print("\n=== Product Information Extraction ===")
    await example_product_extraction()
    
    print("\n=== Meeting Summary ===")
    await example_meeting_summary()
    
    print("\n=== Code Analysis ===")
    await example_code_analysis()
    
    print("\n=== Built-in Functions ===")
    await example_builtin_functions()
    
    print("\n=== Support Ticket Analysis ===")
    await example_support_ticket()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_all_examples()) 