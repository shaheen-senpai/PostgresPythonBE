"""
Main API router that includes all route modules.
"""
from fastapi import APIRouter

from app.views import auth, users, vibe_logs, vibe_reports, burnout_scores

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(vibe_logs.router, prefix="/vibe-logs", tags=["Vibe Logs"])
api_router.include_router(vibe_reports.router, prefix="/vibe-reports", tags=["Vibe Reports"])
api_router.include_router(burnout_scores.router, prefix="/burnout-scores", tags=["Burnout Scores"])
