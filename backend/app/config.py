import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./opportunities.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    FIRECRAWL_API_KEY: str = ""
    
    SENDGRID_API_KEY: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Check if environment is already configured in current env
settings = Settings()
