# Postgres - Python Backend Framework

A robust Python backend framework using FastAPI, SQLAlchemy ORM, and PostgreSQL following MVC architecture.

## Features

- **MVC Architecture**: Clean separation of concerns
- **PostgreSQL Integration**: Direct connection to local PostgreSQL database
- **ORM Support**: SQLAlchemy for database operations
- **Migration System**: Alembic for database migrations
- **Middleware Stack**: Logging, error handling, authentication, etc.
- **API Documentation**: Automatic Swagger/OpenAPI documentation
- **Environment Management**: Configuration for different environments
- **Testing Framework**: Pytest setup for unit and integration tests
- **AI Service**: Simple LLM integration with Google Gemini API using LangChain

## Project Structure

```
app/
├── ai/             # AI service for LLM integration
├── config/         # Configuration files and settings
├── controllers/    # Business logic and request handling
├── middlewares/    # Custom middleware components
├── migrations/     # Database migration scripts
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic schemas for validation
├── tests/          # Test cases
├── utils/          # Helper functions and utilities
└── views/          # API routes and endpoints
```

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional, for containerized PostgreSQL)

### Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd VibeLogBE
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Start PostgreSQL using Docker:

   ```
   docker compose up -d
   ```

5. Set up environment variables:

   ```
   cp .env.example .env
   # Edit .env with your configuration
   # Add GOOGLE_API_KEY=your_api_key for AI features (optional)
   ```

6. Run database migrations:

   ```
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

7. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

## Usage

Access the API documentation at `http://localhost:8000/docs` after starting the server.

### AI Service Usage

The AI service provides enhanced LLM integration with Google Gemini using LangChain:

```python
from app.ai import ai_text, ai_structured, ai_generate, ai_stream
from typing import List

# Simple text generation with model selection
result = await ai_text(
    "Write a haiku about Python",
    system_prompt="You are a creative poet",
    model="gemini-1.5-pro"  # or "gemini-1.5-flash" for faster responses
)

# Structured output with Pydantic models (recommended)
from langchain_core.pydantic_v1 import BaseModel, Field

class SentimentAnalysis(BaseModel):
    sentiment: str = Field(..., description="positive, negative, or neutral")
    confidence: float = Field(..., description="confidence score 0-1")
    keywords: List[str] = Field(..., description="key sentiment words")

analysis = await ai_structured(
    "Analyze sentiment: 'I love this product!'",
    SentimentAnalysis,
    system_prompt="You are a sentiment analyzer",
    model="gemini-1.5-pro"
)
print(analysis.sentiment, analysis.confidence)

# Streaming responses for real-time applications
async for chunk in ai_stream(
    "Write a story about space exploration",
    "You are a creative writer"
):
    print(chunk, end="", flush=True)

# Advanced configuration with safety settings
story = await ai_generate(
    user_prompt="Write a short story about AI",
    system_prompt="You are a creative writer",
    model="gemini-1.5-pro",
    temperature=0.9,
    max_tokens=500
)
```

**Enhanced endpoint integration:**

```python
# In your views/users.py or any endpoint  
from app.ai import ai_text, ai_structured, ai_stream
from fastapi.responses import StreamingResponse
from langchain_core.pydantic_v1 import BaseModel, Field

class FeedbackAnalysis(BaseModel):
    sentiment: str = Field(..., description="overall sentiment")
    issues: List[str] = Field(..., description="identified issues")
    satisfaction_score: float = Field(..., description="score 0-10")
    priority: str = Field(..., description="priority level")

@router.post("/analyze-feedback")
async def analyze_feedback(feedback: str, detailed: bool = False):
    model = "gemini-1.5-pro" if detailed else "gemini-1.5-flash"
    
    return await ai_structured(
        f"Analyze: '{feedback}'",
        FeedbackAnalysis,
        "You are a product analyst",
        model=model
    )

@router.get("/welcome/{username}")
async def welcome_user(username: str, style: str = "friendly"):
    message = await ai_text(
        f"Create {style} welcome message for {username}",
        "You are a customer service representative",
        model="gemini-1.5-flash"  # Fast for simple tasks
    )
    return {"message": message}

@router.get("/generate-content-stream")
async def stream_content(topic: str):
    async def generate():
        async for chunk in ai_stream(f"Write about {topic}", "You are a writer"):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(generate(), media_type="text/plain")
```

**Configuration:**

- Add `GOOGLE_API_KEY` to your `.env` file
- Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- AI service gracefully handles missing API key (logs warning)

## Development

### Creating a New Model

Add a new model in `app/models/` following the SQLAlchemy ORM pattern.

### Adding a New Endpoint

1. Create controller logic in `app/controllers/`
2. Define routes in `app/views/`
3. Register routes in `app/main.py`

### Running Tests

```
pytest
```

## License

[MIT License](LICENSE)
