"""
Database fixtures for tests.
Encapsulated fixtures for database testing with testcontainers.
"""
import pytest
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

from tests.infrastructure.config.settings_test import test_settings
from tests.infrastructure.db.manager import (
    create_engine_and_schema,
    shutdown_backends,
    SchemaStrategy,
)
from tests.infrastructure.db.schema_builders.sqlalchemy_builder import sqlalchemy_strategy
from tests.infrastructure.db.schema_builders.sqlmodel_builder import sqlmodel_strategy
from tests.infrastructure.db.schema_builders.sql_files_builder import sql_files_strategy


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
def db_engine() -> Engine:
    """
    Start Postgres (testcontainers) and prepare schema + seeds once per session.
    
    This fixture:
    - Starts a PostgreSQL container using testcontainers
    - Creates the database schema based on configured strategy
    - Runs seed scripts if configured
    - Provides the engine for the entire test session
    - Cleans up containers after session ends
    """
    strategy = _resolve_schema_strategy()
    engine = create_engine_and_schema(
        strategy=strategy,
        seeds_dir=test_settings.DB_SEEDS_DIR,
    )
    yield engine
    shutdown_backends()


@pytest.fixture()
def db_session(db_engine: Engine) -> Session:
    """
    Provide a SQLAlchemy session per test with transaction scope.
    
    Each test runs in a transaction that is rolled back after the test,
    ensuring test isolation. This fixture:
    - Creates a new session for each test
    - Provides transactional isolation
    - Rolls back all changes after test execution
    - Truncates tables to ensure clean state
    - Closes session properly
    
    Args:
        db_engine: Database engine from session-scoped fixture
        
    Yields:
        SQLAlchemy Session object for the test
    """
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

