"""
Main API router that includes all route modules.
"""
from fastapi import APIRouter

from app.views import auth, users

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
