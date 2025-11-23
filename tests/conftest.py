"""
Global pytest configuration
General test configuration and shared fixtures.
Database-related fixtures are encapsulated in infrastructure/db/fixtures.py
"""
import pytest
from httpx import AsyncClient
from app.main import app

# Register database fixtures module so pytest can discover the fixtures
pytest_plugins = [
    "tests.infrastructure.db.fixtures",
    "tests.infrastructure.external_apis.fixtures",
]


@pytest.fixture
async def client(db_session):
    """
    Async HTTP client for tests with database dependency override.
    
    Overrides the get_db dependency to use the testcontainers database session.
    This allows tests to use a test database without modifying the application code.
    
    Args:
        db_session: Database session fixture from infrastructure/db
        
    Yields:
        AsyncClient: HTTP client configured for testing
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

