"""
Global pytest configuration
"""
import os
import pytest
from httpx import AsyncClient
from app.main import app

# DB manager (encapsulated)
from tests.infrastructure.db.manager import (
    create_engine_and_schema,
    session_scope,
    shutdown_backends,
    SchemaStrategy,
)
from tests.infrastructure.config.settings_test import test_settings
from tests.infrastructure.db.schema_builders.sqlalchemy_builder import sqlalchemy_strategy
from tests.infrastructure.db.schema_builders.sqlmodel_builder import sqlmodel_strategy
from tests.infrastructure.db.schema_builders.sql_files_builder import sql_files_strategy


@pytest.fixture
async def client(db_session):
    """
    Async HTTP client for tests with database dependency override.
    
    Overrides the get_db dependency to use the testcontainers database session.
    """
    from app.database.connection import get_db
    
    def override_get_db():
        """Override get_db to use test session"""
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up override after test
    app.dependency_overrides.clear()


def _resolve_schema_strategy() -> SchemaStrategy:
    """
    Decide schema strategy from settings. Preference order:
      1) SQLALCHEMY_SCHEMA_MODULE
      2) SQLMODEL_SCHEMA_MODULE
      3) SQL_FILES_DIR
    """
    if test_settings.SQLALCHEMY_SCHEMA_MODULE:
        return sqlalchemy_strategy(
            module=test_settings.SQLALCHEMY_SCHEMA_MODULE,
            base_attribute=test_settings.SQLALCHEMY_BASE_ATTRIBUTE,
        )
    if test_settings.SQLMODEL_SCHEMA_MODULE:
        return sqlmodel_strategy(
            module=test_settings.SQLMODEL_SCHEMA_MODULE,
            model_attribute=test_settings.SQLMODEL_ATTRIBUTE,
        )
    if test_settings.SQL_FILES_DIR:
        return sql_files_strategy(test_settings.SQL_FILES_DIR)
    # Default to raw SQL files if none configured (no-op when dir is missing)
    return sql_files_strategy("tests/infrastructure/db/migrations/sql")


@pytest.fixture(scope="session")
def db_engine():
    """
    Start Postgres (testcontainers) and prepare schema + seeds once per session.
    """
    strategy = _resolve_schema_strategy()
    engine = create_engine_and_schema(
        strategy=strategy,
        seeds_dir=test_settings.DB_SEEDS_DIR,
    )
    yield engine
    shutdown_backends()


@pytest.fixture()
def db_session(db_engine):
    """
    Provide a SQLAlchemy session per test with transaction scope.
    Each test runs in a transaction that is rolled back after the test,
    ensuring test isolation.
    """
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text
    
    SessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    
    try:
        yield session
        # Rollback at the end to ensure test isolation
        session.rollback()
    finally:
        # Clean up any remaining data
        try:
            session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

