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


# ==================== POST /users (CREATE) Tests ====================

@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient):
    """
    Test POST /users creates a new user successfully.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    from tests.infrastructure.schemas.user import UserCreateSpec
    
    user_data = UserCreateSpec(
        email="newuser@example.com",
        username="newuser",
        is_active=True
    )
    
    response = await client.post("/users", json=user_data.model_dump())
    
    assert response.status_code == 201
    data = response.json()
    
    # Validate response matches UserSpec
    user = UserSpec(**data)
    assert user.email == "newuser@example.com"
    assert user.username == "newuser"
    assert user.is_active is True
    assert user.id is not None
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient, db_session):
    """
    Test POST /users returns 409 when email already exists.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    from sqlalchemy import text
    from datetime import datetime
    from tests.infrastructure.schemas.user import UserCreateSpec
    
    # Create a user in the database first
    db_session.execute(
        text("""
            INSERT INTO users (email, username, is_active, created_at, updated_at)
            VALUES (:email, :username, :is_active, :created_at, :updated_at)
        """),
        {
            "email": "existing@example.com",
            "username": "existing",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": None
        }
    )
    db_session.commit()
    
    # Try to create another user with the same email
    user_data = UserCreateSpec(
        email="existing@example.com",
        username="newuser",
        is_active=True
    )
    
    response = await client.post("/users", json=user_data.model_dump())
    
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_user_duplicate_username(client: AsyncClient, db_session):
    """
    Test POST /users returns 409 when username already exists.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    from sqlalchemy import text
    from datetime import datetime
    from tests.infrastructure.schemas.user import UserCreateSpec
    
    # Create a user in the database first
    db_session.execute(
        text("""
            INSERT INTO users (email, username, is_active, created_at, updated_at)
            VALUES (:email, :username, :is_active, :created_at, :updated_at)
        """),
        {
            "email": "user1@example.com",
            "username": "existing_username",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": None
        }
    )
    db_session.commit()
    
    # Try to create another user with the same username
    user_data = UserCreateSpec(
        email="user2@example.com",
        username="existing_username",
        is_active=True
    )
    
    response = await client.post("/users", json=user_data.model_dump())
    
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_user_invalid_email_format(client: AsyncClient):
    """
    Test POST /users returns 422 when email format is invalid.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    from tests.infrastructure.schemas.user import UserCreateSpec
    
    user_data = {
        "email": "invalid-email",
        "username": "testuser",
        "is_active": True
    }
    
    response = await client.post("/users", json=user_data)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_user_missing_required_fields(client: AsyncClient):
    """
    Test POST /users returns 422 when required fields are missing.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    # Missing email
    response = await client.post("/users", json={"username": "testuser"})
    assert response.status_code == 422
    
    # Missing username
    response = await client.post("/users", json={"email": "test@example.com"})
    assert response.status_code == 422


# ==================== PUT /users/{id} (UPDATE) Tests ====================

@pytest.mark.asyncio
async def test_update_user_success(client: AsyncClient, db_session):
    """
    Test PUT /users/{id} updates a user successfully.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    from sqlalchemy import text
    from datetime import datetime
    from tests.infrastructure.schemas.user import UserUpdateSpec
    
    # Create a user in the database first
    result = db_session.execute(
        text("""
            INSERT INTO users (email, username, is_active, created_at, updated_at)
            VALUES (:email, :username, :is_active, :created_at, :updated_at)
            RETURNING id
        """),
        {
            "email": "original@example.com",
            "username": "originaluser",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": None
        }
    )
    user_id = result.scalar()
    db_session.commit()
    
    # Update the user
    update_data = UserUpdateSpec(
        email="updated@example.com",
        username="updateduser",
        is_active=False
    )
    
    response = await client.put(f"/users/{user_id}", json=update_data.model_dump(exclude_none=True))
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response matches UserSpec
    user = UserSpec(**data)
    assert user.id == user_id
    assert user.email == "updated@example.com"
    assert user.username == "updateduser"
    assert user.is_active is False
    assert user.updated_at is not None


@pytest.mark.asyncio
async def test_update_user_partial(client: AsyncClient, db_session):
    """
    Test PUT /users/{id} allows partial updates (only some fields).
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    from sqlalchemy import text
    from datetime import datetime
    from tests.infrastructure.schemas.user import UserUpdateSpec
    
    # Create a user in the database first
    result = db_session.execute(
        text("""
            INSERT INTO users (email, username, is_active, created_at, updated_at)
            VALUES (:email, :username, :is_active, :created_at, :updated_at)
            RETURNING id
        """),
        {
            "email": "partial@example.com",
            "username": "partialuser",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": None
        }
    )
    user_id = result.scalar()
    db_session.commit()
    
    # Update only email
    update_data = UserUpdateSpec(email="newemail@example.com")
    
    response = await client.put(f"/users/{user_id}", json=update_data.model_dump(exclude_none=True))
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response
    user = UserSpec(**data)
    assert user.id == user_id
    assert user.email == "newemail@example.com"
    assert user.username == "partialuser"  # Should remain unchanged
    assert user.is_active is True  # Should remain unchanged


@pytest.mark.asyncio
async def test_update_user_not_found(client: AsyncClient):
    """
    Test PUT /users/{id} returns 404 when user doesn't exist.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    from tests.infrastructure.schemas.user import UserUpdateSpec
    
    update_data = UserUpdateSpec(email="test@example.com")
    
    response = await client.put("/users/999", json=update_data.model_dump(exclude_none=True))
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_update_user_duplicate_email(client: AsyncClient, db_session):
    """
    Test PUT /users/{id} returns 409 when new email already exists.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    from sqlalchemy import text
    from datetime import datetime
    from tests.infrastructure.schemas.user import UserUpdateSpec
    
    # Create two users
    result1 = db_session.execute(
        text("""
            INSERT INTO users (email, username, is_active, created_at, updated_at)
            VALUES (:email, :username, :is_active, :created_at, :updated_at)
            RETURNING id
        """),
        {
            "email": "user1@example.com",
            "username": "user1",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": None
        }
    )
    user1_id = result1.scalar()
    
    result2 = db_session.execute(
        text("""
            INSERT INTO users (email, username, is_active, created_at, updated_at)
            VALUES (:email, :username, :is_active, :created_at, :updated_at)
            RETURNING id
        """),
        {
            "email": "user2@example.com",
            "username": "user2",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": None
        }
    )
    user2_id = result2.scalar()
    db_session.commit()
    
    # Try to update user2 with user1's email
    update_data = UserUpdateSpec(email="user1@example.com")
    
    response = await client.put(f"/users/{user2_id}", json=update_data.model_dump(exclude_none=True))
    
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data


# ==================== DELETE /users/{id} Tests ====================

@pytest.mark.asyncio
async def test_delete_user_success(client: AsyncClient, db_session):
    """
    Test DELETE /users/{id} deletes a user successfully.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    from sqlalchemy import text
    from datetime import datetime
    
    # Create a user in the database first
    result = db_session.execute(
        text("""
            INSERT INTO users (email, username, is_active, created_at, updated_at)
            VALUES (:email, :username, :is_active, :created_at, :updated_at)
            RETURNING id
        """),
        {
            "email": "todelete@example.com",
            "username": "todelete",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": None
        }
    )
    user_id = result.scalar()
    db_session.commit()
    
    # Delete the user
    response = await client.delete(f"/users/{user_id}")
    
    assert response.status_code == 204
    
    # Verify user is deleted
    get_response = await client.get(f"/users/{user_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_not_found(client: AsyncClient):
    """
    Test DELETE /users/{id} returns 404 when user doesn't exist.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    response = await client.delete("/users/999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_delete_user_invalid_id_format(client: AsyncClient):
    """
    Test DELETE /users/{id} returns 422 when ID is not a valid integer.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    response = await client.delete("/users/invalid-id")
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

