"""
Error handling middleware for consistent error responses.
"""
import traceback
from typing import Callable, Dict, Any, Union

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling and formatting errors."""

    def __init__(self, app: ASGIApp):
        """Initialize the middleware."""
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and handle any errors."""
        try:
            return await call_next(request)
        except Exception as exc:
            return await self.handle_exception(request, exc)

    async def handle_exception(self, request: Request, exc: Exception) -> Response:
        """Handle exceptions and return appropriate responses."""
        # Get request ID if available
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Log the exception with traceback
        logger.error(
            f"Unhandled exception | Request ID: {request_id} | "
            f"Path: {request.url.path} | Error: {str(exc)}"
        )
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        
        # Prepare error response
        error_response = self.format_error_response(exc, request_id)
        
        # Determine status code based on exception type
        status_code = self.get_status_code(exc)
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
        )
    
    def format_error_response(self, exc: Exception, request_id: str) -> Dict[str, Any]:
        """Format the error response."""
        return {
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
                "request_id": request_id,
            }
        }
    
    def get_status_code(self, exc: Exception) -> int:
        """Determine the appropriate status code based on exception type."""
        # Map exception types to status codes
        exception_map = {
            # Authentication errors
            "AuthenticationError": status.HTTP_401_UNAUTHORIZED,
            "NotAuthenticatedError": status.HTTP_401_UNAUTHORIZED,
            
            # Authorization errors
            "PermissionDeniedError": status.HTTP_403_FORBIDDEN,
            "ForbiddenError": status.HTTP_403_FORBIDDEN,
            
            # Not found errors
            "NotFoundError": status.HTTP_404_NOT_FOUND,
            
            # Validation errors
            "ValidationError": status.HTTP_422_UNPROCESSABLE_ENTITY,
            
            # Conflict errors
            "ConflictError": status.HTTP_409_CONFLICT,
            
            # Rate limit errors
            "RateLimitExceededError": status.HTTP_429_TOO_MANY_REQUESTS,
        }
        
        # Get exception class name
        exc_name = exc.__class__.__name__
        
        # Return mapped status code or default to 500
        return exception_map.get(exc_name, status.HTTP_500_INTERNAL_SERVER_ERROR)
