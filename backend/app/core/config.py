from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
from typing import List
import re
import logging

class Settings(BaseSettings):
    # Banco
    database_url: str = Field(..., description="PostgreSQL connection string")
    
    # Redis
    redis_url: str = Field(..., description="Redis connection string")
    
    # Segurança
    secret_key: str = Field(..., min_length=32, description="Secret key for JWT signing (minimum 32 characters)")
    admin_username: str = Field(..., description="Admin username for basic authentication")
    admin_password: str = Field(..., min_length=8, description="Admin password (minimum 8 characters)")
    
    # CORS
    backend_cors_origins: List[str] = Field(default=["http://localhost", "http://localhost:3000"], description="Allowed CORS origins")
    
    # Polling
    poll_interval: int = Field(default=60, gt=0, description="Polling interval in seconds (must be positive)")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

    @field_validator('database_url', 'redis_url')
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        # Basic URL validation - can be extended as needed
        if not v.startswith(('http://', 'https://', 'postgresql://', 'postgresql+asyncpg://', 'redis://', 'rediss://')):
            raise ValueError('Must be a valid URL')
        return v

    @field_validator('backend_cors_origins', mode='before')
    @classmethod
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            # Handle comma-separated string from environment variable
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()