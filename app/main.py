"""
Main application entry point for the VibeLogBE framework.
"""
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.middlewares.logging_middleware import LoggingMiddleware
from app.middlewares.error_middleware import ErrorHandlerMiddleware
from app.views.api import api_router
from app.utils.logger import setup_logging

# Create FastAPI application
app = FastAPI(
    title="VibeLogBE",
    description="A robust Python backend framework with PostgreSQL",
    version="0.1.0",
)

# Setup logging
setup_logging()

# Add middlewares
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=get_settings().HOST,
        port=get_settings().PORT,
        reload=get_settings().DEBUG,
    )
