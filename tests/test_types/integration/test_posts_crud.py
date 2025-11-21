"""
Integration tests for Posts CRUD operations.
Following TDD: tests are written first, implementation comes later.

These tests mock an external API and use assets from tests/infrastructure/external_apis/assets/posts/
to ensure consistent test data without centralizing the mock definition.
The assets are loaded dynamically at test execution time.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

from tests.infrastructure.schemas.post import PostSpec, PostCreateSpec, PostUpdateSpec
from tests.infrastructure.external_apis.posts.mock import PostsMock


@pytest.fixture
def posts_mock():
    """Fixture that provides PostsMock instance for loading assets"""
    return PostsMock()


@pytest.fixture
def mock_external_api(posts_mock):
    """
    Fixture that mocks the external Posts API.
    Returns mock responses based on assets loaded from infrastructure/external_apis/assets/posts/
    """
    # Track deleted posts to maintain state across calls
    deleted_posts = set()
    
    with patch('app.services.posts_service.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_client)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_context_manager
        
        # Configure mock responses based on assets
        async def mock_get(url, **kwargs):
            mock_response = MagicMock()
            
            if url.endswith("/posts"):
                # GET all posts
                data = posts_mock.get_all_posts()
                mock_response.status_code = 200
                mock_response.json = MagicMock(return_value=data)
                mock_response.raise_for_status = MagicMock()
            elif "/posts/" in url:
                # GET post by ID
                post_id = int(url.split("/posts/")[-1])
                
                # Check if post was deleted
                if post_id in deleted_posts:
                    from httpx import HTTPStatusError
                    error_data = posts_mock.get_not_found_error()
                    mock_response.status_code = 404
                    mock_response.json = MagicMock(return_value=error_data)
                    mock_response.raise_for_status = MagicMock(
                        side_effect=HTTPStatusError(
                            "404 Not Found",
                            request=MagicMock(),
                            response=MagicMock(status_code=404)
                        )
                    )
                else:
                    data = posts_mock.get_post_by_id(post_id)
                    
                    if data:
                        mock_response.status_code = 200
                        mock_response.json = MagicMock(return_value=data)
                        mock_response.raise_for_status = MagicMock()
                    else:
                        # Post not found - raise HTTPStatusError for 404
                        from httpx import HTTPStatusError
                        error_data = posts_mock.get_not_found_error()
                        mock_response.status_code = 404
                        mock_response.json = MagicMock(return_value=error_data)
                        mock_response.raise_for_status = MagicMock(
                            side_effect=HTTPStatusError(
                                "404 Not Found",
                                request=MagicMock(),
                                response=MagicMock(status_code=404)
                            )
                        )
            else:
                from httpx import HTTPStatusError
                mock_response.status_code = 404
                mock_response.json = MagicMock(return_value={"error": "Not found"})
                mock_response.raise_for_status = MagicMock(
                    side_effect=HTTPStatusError(
                        "404 Not Found",
                        request=MagicMock(),
                        response=MagicMock(status_code=404)
                    )
                )
            
            return mock_response
        
        async def mock_post(url, json=None, **kwargs):
            mock_response = MagicMock()
            
            if url.endswith("/posts"):
                # POST create post
                data = posts_mock.get_create_response()
                mock_response.status_code = 201
                mock_response.json = MagicMock(return_value=data)
                mock_response.raise_for_status = MagicMock()
            else:
                from httpx import HTTPStatusError
                mock_response.status_code = 404
                mock_response.json = MagicMock(return_value={"error": "Not found"})
                mock_response.raise_for_status = MagicMock(
                    side_effect=HTTPStatusError(
                        "404 Not Found",
                        request=MagicMock(),
                        response=MagicMock(status_code=404)
                    )
                )
            
            return mock_response
        
        async def mock_put(url, json=None, **kwargs):
            mock_response = MagicMock()
            
            if "/posts/" in url:
                post_id = int(url.split("/posts/")[-1])
                
                # Check if post was deleted
                if post_id in deleted_posts:
                    from httpx import HTTPStatusError
                    error_data = posts_mock.get_not_found_error()
                    mock_response.status_code = 404
                    mock_response.json = MagicMock(return_value=error_data)
                    mock_response.raise_for_status = MagicMock(
                        side_effect=HTTPStatusError(
                            "404 Not Found",
                            request=MagicMock(),
                            response=MagicMock(status_code=404)
                        )
                    )
                else:
                    existing_post = posts_mock.get_post_by_id(post_id)
                    
                    if existing_post:
                        # Update successful - merge existing post with update data
                        update_data = json if json else {}
                        # Start with existing post data
                        data = existing_post.copy()
                        # Apply only provided fields (partial update)
                        data.update({k: v for k, v in update_data.items() if v is not None})
                        data["id"] = post_id  # Ensure ID matches
                        # Update timestamp if any field changed
                        if update_data:
                            from datetime import datetime, timezone
                            data["updatedAt"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        mock_response.status_code = 200
                        mock_response.json = MagicMock(return_value=data)
                        mock_response.raise_for_status = MagicMock()
                    else:
                        # Post not found
                        from httpx import HTTPStatusError
                        error_data = posts_mock.get_not_found_error()
                        mock_response.status_code = 404
                        mock_response.json = MagicMock(return_value=error_data)
                        mock_response.raise_for_status = MagicMock(
                            side_effect=HTTPStatusError(
                                "404 Not Found",
                                request=MagicMock(),
                                response=MagicMock(status_code=404)
                            )
                        )
            else:
                from httpx import HTTPStatusError
                mock_response.status_code = 404
                mock_response.json = MagicMock(return_value={"error": "Not found"})
                mock_response.raise_for_status = MagicMock(
                    side_effect=HTTPStatusError(
                        "404 Not Found",
                        request=MagicMock(),
                        response=MagicMock(status_code=404)
                    )
                )
            
            return mock_response
        
        async def mock_delete(url, **kwargs):
            mock_response = MagicMock()
            
            if "/posts/" in url:
                post_id = int(url.split("/posts/")[-1])
                
                # Check if already deleted
                if post_id in deleted_posts:
                    from httpx import HTTPStatusError
                    error_data = posts_mock.get_not_found_error()
                    mock_response.status_code = 404
                    mock_response.json = MagicMock(return_value=error_data)
                    mock_response.raise_for_status = MagicMock(
                        side_effect=HTTPStatusError(
                            "404 Not Found",
                            request=MagicMock(),
                            response=MagicMock(status_code=404)
                        )
                    )
                else:
                    existing_post = posts_mock.get_post_by_id(post_id)
                    
                    if existing_post:
                        # Delete successful - mark as deleted
                        deleted_posts.add(post_id)
                        mock_response.status_code = 204
                        mock_response.json = MagicMock(return_value=None)
                        mock_response.raise_for_status = MagicMock()
                    else:
                        # Post not found
                        from httpx import HTTPStatusError
                        error_data = posts_mock.get_not_found_error()
                        mock_response.status_code = 404
                        mock_response.json = MagicMock(return_value=error_data)
                        mock_response.raise_for_status = MagicMock(
                            side_effect=HTTPStatusError(
                                "404 Not Found",
                                request=MagicMock(),
                                response=MagicMock(status_code=404)
                            )
                        )
            else:
                from httpx import HTTPStatusError
                mock_response.status_code = 404
                mock_response.json = MagicMock(return_value={"error": "Not found"})
                mock_response.raise_for_status = MagicMock(
                    side_effect=HTTPStatusError(
                        "404 Not Found",
                        request=MagicMock(),
                        response=MagicMock(status_code=404)
                    )
                )
            
            return mock_response
        
        mock_client.get = mock_get
        mock_client.post = mock_post
        mock_client.put = mock_put
        mock_client.delete = mock_delete
        
        yield mock_client


# ==================== GET /posts Tests ====================

@pytest.mark.asyncio
async def test_get_all_posts_success(client: AsyncClient, mock_external_api, posts_mock):
    """
    Test GET /posts returns all posts from external API.
    
    RED phase: This test will fail because:
    - The endpoint doesn't exist yet
    - The service doesn't exist yet
    
    This test uses assets loaded from tests/infrastructure/external_apis/assets/posts/
    """
    response = await client.get("/posts")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response is a list
    assert isinstance(data, list)
    
    # Validate each post matches PostSpec specification
    # This ensures the app response satisfies the expected contract
    expected_posts = posts_mock.get_all_posts()
    assert len(data) == len(expected_posts)
    
    for post_data in data:
        post = PostSpec(**post_data)
        assert post.id > 0
        assert post.title
        assert post.body
        assert post.userId > 0
        assert post.createdAt


@pytest.mark.asyncio
async def test_get_post_by_id_success(client: AsyncClient, mock_external_api, posts_mock):
    """
    Test GET /posts/{id} returns post by ID from external API.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    post_id = 1
    response = await client.get(f"/posts/{post_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response matches PostSpec specification
    post = PostSpec(**data)
    
    # Validate specific business logic using assets
    expected_post = posts_mock.get_post_by_id(post_id)
    assert post.id == expected_post["id"]
    assert post.title == expected_post["title"]
    assert post.body == expected_post["body"]
    assert post.userId == expected_post["userId"]


@pytest.mark.asyncio
async def test_get_post_by_id_not_found(client: AsyncClient, mock_external_api):
    """
    Test GET /posts/{id} returns 404 when post doesn't exist.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    post_id = 999
    response = await client.get(f"/posts/{post_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data or "error" in data


@pytest.mark.asyncio
async def test_get_post_invalid_id_format(client: AsyncClient):
    """
    Test GET /posts/{id} returns 422 when ID is not a valid integer.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    response = await client.get("/posts/invalid-id")
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


# ==================== POST /posts (CREATE) Tests ====================

@pytest.mark.asyncio
async def test_create_post_success(client: AsyncClient, mock_external_api, posts_mock):
    """
    Test POST /posts creates a new post via external API.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    # Use create request from assets
    post_data = posts_mock.get_create_request()
    
    response = await client.post("/posts", json=post_data)
    
    assert response.status_code == 201
    data = response.json()
    
    # Validate response matches PostSpec
    post = PostSpec(**data)
    
    # Validate specific business logic using assets
    expected_response = posts_mock.get_create_response()
    assert post.title == expected_response["title"]
    assert post.body == expected_response["body"]
    assert post.userId == expected_response["userId"]
    assert post.id > 0
    assert post.createdAt


@pytest.mark.asyncio
async def test_create_post_missing_required_fields(client: AsyncClient):
    """
    Test POST /posts returns 422 when required fields are missing.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    # Missing title
    response = await client.post("/posts", json={"body": "Test body", "userId": 1})
    assert response.status_code == 422
    
    # Missing body
    response = await client.post("/posts", json={"title": "Test title", "userId": 1})
    assert response.status_code == 422
    
    # Missing userId
    response = await client.post("/posts", json={"title": "Test title", "body": "Test body"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_post_invalid_user_id_format(client: AsyncClient):
    """
    Test POST /posts returns 422 when userId is not a valid integer.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    post_data = {
        "title": "Test Post",
        "body": "Test body",
        "userId": "invalid"
    }
    
    response = await client.post("/posts", json=post_data)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


# ==================== PUT /posts/{id} (UPDATE) Tests ====================

@pytest.mark.asyncio
async def test_update_post_success(client: AsyncClient, mock_external_api, posts_mock):
    """
    Test PUT /posts/{id} updates a post via external API.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    post_id = 1
    # Use update request from assets
    update_data = posts_mock.get_update_request()
    
    response = await client.put(f"/posts/{post_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response matches PostSpec
    post = PostSpec(**data)
    assert post.id == post_id
    assert post.title == update_data["title"]
    assert post.body == update_data["body"]
    assert post.updatedAt is not None  # Should have updated timestamp


@pytest.mark.asyncio
async def test_update_post_partial(client: AsyncClient, mock_external_api, posts_mock):
    """
    Test PUT /posts/{id} allows partial updates (only some fields).
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    post_id = 1
    # Update only title
    update_data = {"title": "Updated Title Only"}
    
    response = await client.put(f"/posts/{post_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response
    post = PostSpec(**data)
    assert post.id == post_id
    assert post.title == "Updated Title Only"
    # Body should remain from original post
    original_post = posts_mock.get_post_by_id(post_id)
    assert post.body == original_post["body"]


@pytest.mark.asyncio
async def test_update_post_not_found(client: AsyncClient, mock_external_api):
    """
    Test PUT /posts/{id} returns 404 when post doesn't exist.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    post_id = 999
    update_data = {"title": "Updated Title"}
    
    response = await client.put(f"/posts/{post_id}", json=update_data)
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data or "error" in data


@pytest.mark.asyncio
async def test_update_post_invalid_id_format(client: AsyncClient):
    """
    Test PUT /posts/{id} returns 422 when ID is not a valid integer.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    update_data = {"title": "Updated Title"}
    
    response = await client.put("/posts/invalid-id", json=update_data)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


# ==================== DELETE /posts/{id} Tests ====================

@pytest.mark.asyncio
async def test_delete_post_success(client: AsyncClient, mock_external_api):
    """
    Test DELETE /posts/{id} deletes a post via external API.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    post_id = 1
    
    response = await client.delete(f"/posts/{post_id}")
    
    assert response.status_code == 204
    
    # Verify post is deleted (should return 404)
    get_response = await client.get(f"/posts/{post_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_post_not_found(client: AsyncClient, mock_external_api):
    """
    Test DELETE /posts/{id} returns 404 when post doesn't exist.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    post_id = 999
    response = await client.delete(f"/posts/{post_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data or "error" in data


@pytest.mark.asyncio
async def test_delete_post_invalid_id_format(client: AsyncClient):
    """
    Test DELETE /posts/{id} returns 422 when ID is not a valid integer.
    
    RED phase: This test will fail because the endpoint doesn't exist yet.
    """
    response = await client.delete("/posts/invalid-id")
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

