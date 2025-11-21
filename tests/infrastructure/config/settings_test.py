"""
Test-specific configuration
Loads exclusively from tests/.env.test - no default values.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class TestSettings(BaseSettings):
    """
    Configuration for testing environment.
    All settings are loaded exclusively from tests/.env.test.
    No default values are used - configuration must be explicit.
    """
    
    model_config = SettingsConfigDict(
        env_file="tests/.env.test",
        case_sensitive=True,
        extra="ignore",  # Ignore unknown env vars to allow flexible test configs
    )
    
    # API
    API_HOST: str
    API_PORT: int
    
    # Database backend selection
    TEST_DB_BACKEND: str
    
    # Database credentials (required, no defaults)
    TEST_DB_USER: str
    TEST_DB_PASSWORD: str
    TEST_DB_NAME: str
    TEST_DB_CONTAINER_NAME: str
    
    # Database configuration
    KEEP_TEST_DB: str = "0"  # "0" or "1"
    TEST_DB_PORT: Optional[str] = None  # Optional fixed port
    
    # Seeds directory (optional)
    DB_SEEDS_DIR: Optional[str] = None
    
    # Schema strategy config - select one at a time
    # Examples:
    #   SQLALCHEMY_SCHEMA_MODULE="app.infrastructure.database.models"
    #   SQLALCHEMY_BASE_ATTRIBUTE="Base"
    SQLALCHEMY_SCHEMA_MODULE: Optional[str] = None
    SQLALCHEMY_BASE_ATTRIBUTE: str = "Base"
    #   SQLMODEL_SCHEMA_MODULE="app.infrastructure.database.sqlmodel_models"
    #   SQLMODEL_ATTRIBUTE="SQLModel"
    SQLMODEL_SCHEMA_MODULE: Optional[str] = None
    SQLMODEL_ATTRIBUTE: str = "SQLModel"
    #   SQL_FILES_DIR="tests/infrastructure/db/migrations/sql"
    SQL_FILES_DIR: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "test"
    DEBUG: bool = True


test_settings = TestSettings()

