"""
Neuro-Logistics Configuration

Minimal configuration for the AI-powered logistics system.
No database or Google Maps dependencies.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # Gemini AI (Google)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    GEMINI_TEMPERATURE: float = 0.7
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
