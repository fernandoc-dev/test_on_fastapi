"""
Integration tests for User CRUD operations.
Following TDD: tests are written first, implementation comes later.

These tests use UserSpec from tests.infrastructure.schemas.user,
which is the independent specification model. This ensures tests
validate that the app satisfies requirements, not just internal consistency.
"""
import pytest
from httpx import AsyncClient
from app.main import app
from tests.infrastructure.schemas.user import UserSpec


@pytest.mark.asyncio
async def test_get_users_empty_list_when_no_users(client: AsyncClient):
    """
    Test GET /users returns empty list when no users exist.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    response = await client.get("/users")
    
    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(client: AsyncClient):
    """
    Test GET /users/{id} returns 404 when user doesn't exist.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    response = await client.get("/users/999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_user_by_id_success(client: AsyncClient, db_session):
    """
    Test GET /users/{id} returns user when it exists.
    
    This test will:
    1. Create a user in the database (using raw SQL for now)
    2. Call GET /users/{id}
    3. Verify the response matches the User schema
    
    RED phase: This test will fail because:
    - The endpoint doesn't exist
    - We need to create the user in DB first
    """
    from sqlalchemy import text
    from datetime import datetime
    
    # Create a user directly in the database
    result = db_session.execute(
        text("""
            INSERT INTO users (email, username, is_active, created_at, updated_at)
            VALUES (:email, :username, :is_active, :created_at, :updated_at)
            RETURNING id
        """),
        {
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": None
        }
    )
    user_id = result.scalar()
    db_session.commit()
    
    # Now test the GET endpoint
    response = await client.get(f"/users/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response matches UserSpec specification
    # This ensures the app response satisfies the expected contract
    user = UserSpec(**data)
    
    # Validate specific business logic
    assert user.id == user_id
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_active is True
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_get_users_list_with_multiple_users(client: AsyncClient, db_session):
    """
    Test GET /users returns list of all users.
    
    This test will:
    1. Create multiple users in the database
    2. Call GET /users
    3. Verify all users are returned in correct format
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    from sqlalchemy import text
    from datetime import datetime
    
    # Create multiple users
    users_data = [
        ("user1@example.com", "user1", True),
        ("user2@example.com", "user2", True),
        ("user3@example.com", "user3", False),
    ]
    
    created_ids = []
    for email, username, is_active in users_data:
        result = db_session.execute(
            text("""
                INSERT INTO users (email, username, is_active, created_at, updated_at)
                VALUES (:email, :username, :is_active, :created_at, :updated_at)
                RETURNING id
            """),
            {
                "email": email,
                "username": username,
                "is_active": is_active,
                "created_at": datetime.now(),
                "updated_at": None
            }
        )
        created_ids.append(result.scalar())
    db_session.commit()
    
    # Test GET /users
    response = await client.get("/users")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return all users
    assert len(data) >= len(users_data)  # At least our created users
    
    # Validate each user matches UserSpec specification
    # This ensures all users in the response satisfy the expected contract
    users = [UserSpec(**item) for item in data]
    
    # Verify our created users are in the response
    # (business logic validation)
    user_emails = {user.email for user in users}
    assert "user1@example.com" in user_emails
    assert "user2@example.com" in user_emails
    assert "user3@example.com" in user_emails


@pytest.mark.asyncio
async def test_get_user_invalid_id_format(client: AsyncClient):
    """
    Test GET /users/{id} returns 422 when ID is not a valid integer.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    response = await client.get("/users/invalid-id")
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

