"""
Simple AI Service for LLM integration using LangChain and Gemini API.
"""
import json
import asyncio
from typing import Dict, Any, Optional, Union, List, AsyncGenerator, Type
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.pydantic_v1 import BaseModel as PydanticBaseModel, Field
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.config.settings import get_settings
from app.utils.logger import logger


class AIService:
    """
    Simple AI Service class for LLM tasks with enhanced structured output support.
    
    Usage:
        ai = AIService()
        
        # Simple text generation
        response = await ai.generate(
            user_prompt="Write a haiku about coding",
            system_prompt="You are a creative poet"
        )
        
        # Structured output with Pydantic models
        class SentimentAnalysis(BaseModel):
            sentiment: str = Field(..., description="The sentiment (positive/negative/neutral)")
            confidence: float = Field(..., description="Confidence score 0-1")
        
        result = await ai.generate_structured(
            user_prompt="Analyze sentiment: 'I love this product!'",
            system_prompt="You are a sentiment analyzer",
            output_model=SentimentAnalysis
        )
    """
    
    def __init__(self):
        self.settings = get_settings()
        self._llm = None
        self._initialize()

    def _initialize(self):
        """Initialize the LLM client with proper safety settings."""
        if not self.settings.GOOGLE_API_KEY:
            logger.warning(
                "GOOGLE_API_KEY not found. AI service will not be available.")
            return
        
        try:
            # Configure safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            self._llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=self.settings.GOOGLE_API_KEY,
                temperature=0.7,
                max_output_tokens=2048,
                safety_settings=safety_settings,
                convert_system_message_to_human=True  # For better system message handling
            )
            logger.info("AI Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            self._llm = None

    def _create_chat_prompt(self, system_prompt: Optional[str] = None) -> ChatPromptTemplate:
        """Create a ChatPromptTemplate with optional system message."""
        if system_prompt:
            return ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template("{user_prompt}")
            ])
        else:
            return ChatPromptTemplate.from_messages([
                HumanMessagePromptTemplate.from_template("{user_prompt}")
            ])

    async def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: str = "gemini-1.5-pro"
    ) -> str:
        """
        Generate simple text response using ChatPromptTemplate.
        
        Args:
            user_prompt: The user's input prompt
            system_prompt: Optional system prompt to guide behavior
            temperature: Creativity level (0.0-2.0)
            max_tokens: Maximum tokens to generate
            model: Model to use (gemini-1.5-pro, gemini-1.5-flash, etc.)
        
        Returns:
            Generated response as string
        
        Raises:
            Exception: If AI service is not available or generation fails
        """
        if not self._llm:
            raise Exception(
                "AI service not initialized. Check GOOGLE_API_KEY in settings.")
        
        try:
            # Configure safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            # Configure LLM with custom parameters if different from default
            if temperature != 0.7 or max_tokens != 2048 or model != "gemini-1.5-pro":
                llm = ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=self.settings.GOOGLE_API_KEY,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    safety_settings=safety_settings,
                    convert_system_message_to_human=True
                )
            else:
                llm = self._llm
            
            # Create and use ChatPromptTemplate
            prompt_template = self._create_chat_prompt(system_prompt)
            
            # Create the chain
            chain = prompt_template | llm
            
            # Generate response
            response = await chain.ainvoke({"user_prompt": user_prompt})
            
            return response.content
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            raise Exception(f"AI generation failed: {str(e)}")

    async def generate_structured(
        self,
        user_prompt: str,
        output_model: Type[PydanticBaseModel],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: str = "gemini-1.5-pro"
    ) -> PydanticBaseModel:
        """
        Generate structured output using Pydantic models with ChatPromptTemplate.
        
        Args:
            user_prompt: The user's input prompt
            output_model: Pydantic model class defining the expected output structure
            system_prompt: Optional system prompt to guide behavior
            temperature: Creativity level (0.0-2.0)
            max_tokens: Maximum tokens to generate
            model: Model to use
        
        Returns:
            Instance of the output_model with parsed data
        
        Raises:
            Exception: If AI service is not available or generation fails
        """
        if not self._llm:
            raise Exception(
                "AI service not initialized. Check GOOGLE_API_KEY in settings.")
        
        try:
            # Configure safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            # Configure LLM with custom parameters
            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=self.settings.GOOGLE_API_KEY,
                temperature=temperature,
                max_output_tokens=max_tokens,
                safety_settings=safety_settings,
                convert_system_message_to_human=True
            )
            
            # Use LangChain's structured output feature
            structured_llm = llm.with_structured_output(output_model)
            
            # Create ChatPromptTemplate for structured output
            prompt_template = self._create_chat_prompt(system_prompt)

            # Create the chain: prompt -> structured_llm
            chain = prompt_template | structured_llm

            # Generate structured response
            result = await chain.ainvoke({"user_prompt": user_prompt})

            return result
            
        except Exception as e:
            logger.error(f"Structured AI generation failed: {e}")
            raise Exception(f"Structured AI generation failed: {str(e)}")

    async def generate_json(
        self,
        user_prompt: str,
        schema: Dict[str, str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate JSON output using schema (legacy method, use generate_structured instead).
        
        Args:
            user_prompt: The user's input prompt
            schema: JSON schema {"field": "type", ...}
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
        
        Returns:
            Parsed JSON response as dictionary
        """
        # Create dynamic Pydantic model from schema
        fields = {}
        for field_name, field_type in schema.items():
            if field_type.lower() == "string":
                fields[field_name] = (
                    str, Field(..., description=f"{field_name} as string"))
            elif field_type.lower() == "number":
                fields[field_name] = (
                    float, Field(..., description=f"{field_name} as number"))
            elif field_type.lower() == "boolean":
                fields[field_name] = (
                    bool, Field(..., description=f"{field_name} as boolean"))
            elif field_type.lower() == "array":
                fields[field_name] = (
                    List[str], Field(..., description=f"{field_name} as array"))
            else:
                fields[field_name] = (
                    str, Field(..., description=f"{field_name} as string"))
        
        # Create dynamic model
        DynamicModel = type('DynamicModel', (PydanticBaseModel,), fields)
        
        # Use structured generation
        result = await self.generate_structured(
            user_prompt=user_prompt,
            output_model=DynamicModel,
            system_prompt=system_prompt,
            **kwargs
        )
        
        return result.dict()

    async def generate_stream(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming AI response using ChatPromptTemplate.
        
        Args:
            user_prompt: The user's input prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
            
        Yields:
            Chunks of generated text
        """
        if not self._llm:
            raise Exception(
                "AI service not initialized. Check GOOGLE_API_KEY in settings.")
        
        try:
            # Create ChatPromptTemplate for streaming
            prompt_template = self._create_chat_prompt(system_prompt)
            
            # Create the chain
            chain = prompt_template | self._llm
            
            # Stream the response
            async for chunk in chain.astream({"user_prompt": user_prompt}):
                if chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            logger.error(f"AI streaming failed: {e}")
            raise Exception(f"AI streaming failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self._llm is not None

    async def simple_text(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """
        Simple text generation helper.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
        
        Returns:
            Generated text
        """
        return await self.generate(
            user_prompt=prompt,
            system_prompt=system_prompt,
            **kwargs
        )

    async def structured_output(
        self, 
        prompt: str, 
        output_model: Type[PydanticBaseModel], 
        system_prompt: str = None,
        **kwargs
    ) -> PydanticBaseModel:
        """
        Generate structured output using Pydantic models.
        
        Args:
            prompt: User prompt
            output_model: Pydantic model class
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
        
        Returns:
            Instance of output_model with parsed data
        """
        return await self.generate_structured(
            user_prompt=prompt,
            output_model=output_model,
            system_prompt=system_prompt,
            **kwargs
        )

    def get_available_models(self) -> List[str]:
        """Get list of available Gemini models."""
        return [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro-vision",
            "gemini-2.0-flash",
            "gemini-pro"
        ]


# Pydantic Models for Common Use Cases
class SentimentAnalysis(PydanticBaseModel):
    """Sentiment analysis result."""
    sentiment: str = Field(...,
                           description="The sentiment: positive, negative, or neutral")
    confidence: float = Field(...,
                              description="Confidence score between 0 and 1")
    keywords: List[str] = Field(...,
                                description="Key words that influenced the sentiment")


class PersonInfo(PydanticBaseModel):
    """Information about a person."""
    name: str = Field(..., description="The person's full name")
    age: Optional[int] = Field(None, description="The person's age in years")
    profession: Optional[str] = Field(
        None, description="The person's profession or job title")
    location: Optional[str] = Field(
        None, description="The person's location or city")


class ContentAnalysis(PydanticBaseModel):
    """Content analysis and moderation result."""
    is_safe: bool = Field(...,
                          description="Whether the content is safe and appropriate")
    confidence: float = Field(...,
                              description="Confidence in the safety assessment")
    concerns: List[str] = Field(
        default=[], description="List of any safety concerns found")
    severity: str = Field(...,
                          description="Severity level: none, low, medium, high, critical")
    recommended_action: str = Field(...,
                                    description="Recommended action to take")


class FeedbackAnalysis(PydanticBaseModel):
    """User feedback analysis result."""
    overall_sentiment: str = Field(...,
                                   description="Overall sentiment of the feedback")
    sentiment_score: float = Field(...,
                                   description="Sentiment score from -1 to 1")
    key_strengths: List[str] = Field(
        default=[], description="Positive aspects mentioned")
    key_issues: List[str] = Field(
        default=[], description="Problems or issues mentioned")
    severity_level: str = Field(...,
                                description="Issue severity: low, medium, high")
    suggested_actions: List[str] = Field(
        default=[], description="Recommended actions to take")
    user_satisfaction: float = Field(...,
                                     description="Estimated user satisfaction score 0-10")
    categories: List[str] = Field(
        default=[], description="Categories this feedback relates to")


# Global instance
_ai_service_instance: Optional[AIService] = None


def get_ai_service() -> AIService:
    """
    Get global AI service instance.
    
    Returns:
        AIService instance
    """
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance


# Enhanced convenience functions with structured output support
async def ai_generate(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    model: str = "gemini-1.5-pro",
    **kwargs
) -> str:
    """
    Quick AI text generation function.
    
    Usage:
        result = await ai_generate("Write a haiku about Python")
        
        result = await ai_generate(
            "Explain quantum computing",
            system_prompt="You are a physics teacher",
            model="gemini-1.5-flash"
        )
    """
    service = get_ai_service()
    return await service.generate(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        model=model,
        **kwargs
    )


async def ai_text(prompt: str, system_prompt: str = None, model: str = "gemini-1.5-pro", **kwargs) -> str:
    """Quick text generation with model selection."""
    service = get_ai_service()
    return await service.simple_text(prompt, system_prompt, model=model, **kwargs)


async def ai_structured(
    prompt: str, 
    output_model: Type[PydanticBaseModel], 
    system_prompt: str = None, 
    model: str = "gemini-1.5-pro", 
    **kwargs
) -> PydanticBaseModel:
    """
    Quick structured output generation using Pydantic models.
    
    Usage:
        class Person(BaseModel):
            name: str = Field(..., description="Person's name")
            age: int = Field(..., description="Person's age")
        
        result = await ai_structured(
            "Tell me about Albert Einstein",
            Person,
            "Extract person information"
        )
        print(result.name, result.age)
    """
    service = get_ai_service()
    return await service.generate_structured(
        user_prompt=prompt,
        output_model=output_model,
        system_prompt=system_prompt,
        model=model,
        **kwargs
    )


async def ai_json(prompt: str, schema: Dict[str, str], system_prompt: str = None, model: str = "gemini-1.5-pro", **kwargs) -> Dict[str, Any]:
    """Quick JSON generation (legacy, use ai_structured instead)."""
    service = get_ai_service()
    return await service.generate_json(prompt, schema, system_prompt, model=model, **kwargs)


async def ai_stream(prompt: str, system_prompt: str = None) -> AsyncGenerator[str, None]:
    """Quick streaming generation."""
    service = get_ai_service()
    async for chunk in service.generate_stream(prompt, system_prompt):
        yield chunk


# Convenience functions for common use cases
async def ai_sentiment(text: str, model: str = "gemini-1.5-flash") -> SentimentAnalysis:
    """Quick sentiment analysis."""
    return await ai_structured(
        f"Analyze the sentiment of this text: '{text}'",
        SentimentAnalysis,
        "You are a sentiment analysis expert",
        model=model
    )


async def ai_extract_person(text: str, model: str = "gemini-1.5-flash") -> PersonInfo:
    """Quick person information extraction."""
    return await ai_structured(
        f"Extract person information from: '{text}'",
        PersonInfo,
        "Extract all available person information",
        model=model
    )


async def ai_moderate_content(content: str, model: str = "gemini-1.5-pro") -> ContentAnalysis:
    """Quick content moderation."""
    return await ai_structured(
        f"Analyze this content for safety: '{content}'",
        ContentAnalysis,
        "You are a content moderation expert",
        model=model,
        temperature=0.1
    )


async def ai_analyze_feedback(feedback: str, model: str = "gemini-1.5-pro") -> FeedbackAnalysis:
    """Quick feedback analysis."""
    return await ai_structured(
        f"Analyze this user feedback comprehensively: '{feedback}'",
        FeedbackAnalysis,
        "You are a product manager analyzing user feedback",
        model=model
    )
