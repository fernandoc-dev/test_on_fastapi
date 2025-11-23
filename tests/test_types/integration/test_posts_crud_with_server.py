"""
Integration tests for Posts CRUD operations using real HTTP mock server.

This demonstrates how to use the mock HTTP server instead of code-level mocking.
The server runs in a separate process and serves responses from OpenAPI-mapped payloads.
"""
import pytest
from httpx import AsyncClient

from tests.infrastructure.schemas.post import PostSpec, PostCreateSpec, PostUpdateSpec
from tests.infrastructure.external_apis.posts.mock import PostsMock
from tests.infrastructure.external_apis.server import MockAPIServer


@pytest.fixture
def posts_mock():
    """Fixture that provides PostsMock instance for loading assets"""
    return PostsMock()


@pytest.mark.asyncio
async def test_get_all_posts_with_server(client: AsyncClient, posts_mock_server: MockAPIServer, posts_mock):
    """
    Test GET all posts using real HTTP mock server.
    
    This test uses the mock HTTP server instead of code-level mocking,
    making it closer to a real integration test.
    """
    # Get the base URL of the mock server
    mock_base_url = posts_mock_server.get_base_url()
    
    # In a real scenario, you would configure your service to use this URL
    # For this example, we'll make direct requests to the mock server
    import httpx
    
    async with httpx.AsyncClient(base_url=mock_base_url) as mock_client:
        response = await mock_client.get("/posts")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Validate first post against spec
        if data:
            post = PostSpec(**data[0])
            assert post.id is not None
            assert post.title is not None
            assert post.body is not None
        
        # Compare with expected data from mock
        expected_posts = posts_mock.get_all_posts()
        assert len(data) == len(expected_posts)


@pytest.mark.asyncio
async def test_get_post_by_id_with_server(client: AsyncClient, posts_mock_server: MockAPIServer, posts_mock):
    """Test GET post by ID using real HTTP mock server."""
    mock_base_url = posts_mock_server.get_base_url()
    post_id = 1
    
    import httpx
    
    async with httpx.AsyncClient(base_url=mock_base_url) as mock_client:
        response = await mock_client.get(f"/posts/{post_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate against spec
        post = PostSpec(**data)
        assert post.id == post_id
        
        # Compare with expected data
        expected_post = posts_mock.get_post_by_id(post_id)
        assert data["id"] == expected_post["id"]
        assert data["title"] == expected_post["title"]


@pytest.mark.asyncio
async def test_create_post_with_server(client: AsyncClient, posts_mock_server: MockAPIServer, posts_mock):
    """Test POST create post using real HTTP mock server."""
    mock_base_url = posts_mock_server.get_base_url()
    
    import httpx
    
    post_data = posts_mock.get_create_request()
    
    async with httpx.AsyncClient(base_url=mock_base_url) as mock_client:
        response = await mock_client.post("/posts", json=post_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Validate against spec
        post = PostSpec(**data)
        assert post.title == post_data["title"]
        assert post.body == post_data["body"]


@pytest.mark.asyncio
async def test_delete_post_with_server(client: AsyncClient, posts_mock_server: MockAPIServer):
    """
    Test DELETE post using real HTTP mock server.
    
    This test demonstrates state management - after deleting a post,
    subsequent GET requests should return 404.
    """
    mock_base_url = posts_mock_server.get_base_url()
    post_id = 1
    
    import httpx
    
    async with httpx.AsyncClient(base_url=mock_base_url) as mock_client:
        # First, verify post exists
        response = await mock_client.get(f"/posts/{post_id}")
        assert response.status_code == 200
        
        # Delete the post
        response = await mock_client.delete(f"/posts/{post_id}")
        assert response.status_code == 204
        
        # Verify post is now deleted
        response = await mock_client.get(f"/posts/{post_id}")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_post_with_server(client: AsyncClient, posts_mock_server: MockAPIServer, posts_mock):
    """Test PUT update post using real HTTP mock server."""
    mock_base_url = posts_mock_server.get_base_url()
    post_id = 1
    
    import httpx
    
    update_data = posts_mock.get_update_request()
    
    async with httpx.AsyncClient(base_url=mock_base_url) as mock_client:
        response = await mock_client.put(f"/posts/{post_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate against spec
        post = PostSpec(**data)
        assert post.id == post_id
        # Updated fields should be present
        if "title" in update_data:
            assert post.title == update_data["title"]

