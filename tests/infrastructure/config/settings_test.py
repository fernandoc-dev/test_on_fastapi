"""
Test-specific configuration
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    """Configuration for testing environment"""
    
    model_config = SettingsConfigDict(
        env_file="tests/.env.test",
        case_sensitive=True,
        extra="ignore",  # Ignore unknown env vars to allow flexible test configs
    )
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database backend selection (only postgres_testcontainers for now)
    DB_BACKEND: str = os.getenv("TEST_DB_BACKEND", "postgres_testcontainers")
    # Seeds directory (optional)
    DB_SEEDS_DIR: str | None = os.getenv("TEST_DB_SEEDS_DIR", None)
    # Schema strategy config - select one at a time in fixtures/tests
    # Examples:
    #   SQLALCHEMY_SCHEMA_MODULE="app.infrastructure.database.models"
    #   SQLALCHEMY_BASE_ATTRIBUTE="Base"
    SQLALCHEMY_SCHEMA_MODULE: str | None = os.getenv("SQLALCHEMY_SCHEMA_MODULE", None)
    SQLALCHEMY_BASE_ATTRIBUTE: str = os.getenv("SQLALCHEMY_BASE_ATTRIBUTE", "Base")
    #   SQLMODEL_SCHEMA_MODULE="app.infrastructure.database.sqlmodel_models"
    #   SQLMODEL_ATTRIBUTE="SQLModel"
    SQLMODEL_SCHEMA_MODULE: str | None = os.getenv("SQLMODEL_SCHEMA_MODULE", None)
    SQLMODEL_ATTRIBUTE: str = os.getenv("SQLMODEL_ATTRIBUTE", "SQLModel")
    #   SQL_FILES_DIR="tests/infrastructure/db/migrations/sql"
    SQL_FILES_DIR: str | None = os.getenv("SQL_FILES_DIR", None)
    
    # Environment
    ENVIRONMENT: str = "test"
    DEBUG: bool = True


test_settings = TestSettings()

