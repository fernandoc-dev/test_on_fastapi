"""
Test-specific configuration
"""
import os
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """Configuration for testing environment"""
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database
    DATABASE_URL: str = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://test_user:test_pass@localhost:5432/test_db"
    )
    
    # Environment
    ENVIRONMENT: str = "test"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env.test"
        case_sensitive = True


test_settings = TestSettings()

