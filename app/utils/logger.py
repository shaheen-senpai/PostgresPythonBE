"""
Logger utility for application-wide logging.
"""
import sys
from typing import Optional

from loguru import logger

from app.config.settings import get_settings


def setup_logging() -> None:
    """Configure application-wide logging."""
    # Remove default logger
    logger.remove()
    
    # Add console logger with custom format
    logger.add(
        sys.stderr,
        format=get_settings().LOG_FORMAT,
        level=get_settings().LOG_LEVEL,
        backtrace=True,
        diagnose=True,
    )
    
    # Add file logger for errors and above
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="1 week",
        backtrace=True,
        diagnose=True,
    )
    
    # Add file logger for all logs
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level=get_settings().LOG_LEVEL,
        rotation="10 MB",
        retention="3 days",
    )
    
    # Log startup message
    logger.info(f"Logging initialized for {get_settings().APP_NAME}")


def get_logger(name: Optional[str] = None):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Module name, typically __name__
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)
