from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://analytics_user:analytics_password@localhost:5432/analytics_db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Application
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Agent Configuration
    AGENT_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    BATCH_SIZE: int = 100
    
    # Anomaly Detection
    ANOMALY_THRESHOLD: float = 0.7
    ANOMALY_CONFIDENCE: float = 0.8
    
    # Data Processing
    MAX_DATA_POINTS: int = 10000
    DATA_RETENTION_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
