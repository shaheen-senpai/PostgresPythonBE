"""
Application settings and configuration management.
"""
import os
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings
from pydantic import field_validator, PostgresDsn


class Settings(BaseSettings):
    """Application settings."""

    # Core settings
    APP_NAME: str = "VibeLogBE"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    DATABASE_URI: Optional[PostgresDsn] = None

    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]

    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    # AI Service settings (Optional)
    GOOGLE_API_KEY: Optional[str] = None

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        """Construct database URI from components."""
        if isinstance(v, str):
            return v

        values = info.data
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=int(values.get("POSTGRES_PORT")),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
