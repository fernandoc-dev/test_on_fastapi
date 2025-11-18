"""
Posts service - handles communication with external Posts API.
"""
import httpx
from typing import List, Optional, Dict, Any
from app.schemas.post import Post, PostCreate, PostUpdate


class PostsService:
    """Service for interacting with external Posts API"""
    
    def __init__(self, base_url: str = "https://jsonplaceholder.typicode.com"):
        """
        Initialize Posts service.
        
        Args:
            base_url: Base URL of the external Posts API
        """
        self.base_url = base_url
        self.posts_endpoint = f"{base_url}/posts"
    
    async def get_all_posts(self) -> List[Post]:
        """
        Get all posts from external API.
        
        Returns:
            List of Post objects
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(self.posts_endpoint)
            response.raise_for_status()
            data = response.json()
            
            # Convert API response to Post objects
            return [Post(**post) for post in data]
    
    async def get_post_by_id(self, post_id: int) -> Post:
        """
        Get post by ID from external API.
        
        Args:
            post_id: Post ID
            
        Returns:
            Post object
            
        Raises:
            httpx.HTTPStatusError: If post not found (404) or other HTTP error
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.posts_endpoint}/{post_id}")
            response.raise_for_status()
            data = response.json()
            
            return Post(**data)
    
    async def create_post(self, post_data: PostCreate) -> Post:
        """
        Create a new post in external API.
        
        Args:
            post_data: Post creation data
            
        Returns:
            Created Post object
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.posts_endpoint,
                json=post_data.model_dump()
            )
            response.raise_for_status()
            data = response.json()
            
            return Post(**data)
    
    async def update_post(self, post_id: int, post_data: PostUpdate) -> Post:
        """
        Update a post in external API.
        
        Args:
            post_id: Post ID
            post_data: Post update data (partial update supported)
            
        Returns:
            Updated Post object
            
        Raises:
            httpx.HTTPStatusError: If post not found (404) or other HTTP error
        """
        async with httpx.AsyncClient() as client:
            # Only include non-None fields in the update
            update_payload = post_data.model_dump(exclude_none=True)
            
            response = await client.put(
                f"{self.posts_endpoint}/{post_id}",
                json=update_payload
            )
            response.raise_for_status()
            data = response.json()
            
            return Post(**data)
    
    async def delete_post(self, post_id: int) -> None:
        """
        Delete a post from external API.
        
        Args:
            post_id: Post ID
            
        Raises:
            httpx.HTTPStatusError: If post not found (404) or other HTTP error
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.posts_endpoint}/{post_id}")
            response.raise_for_status()


# Singleton instance
_posts_service: Optional[PostsService] = None


def get_posts_service() -> PostsService:
    """
    Get Posts service instance (singleton).
    
    Returns:
        PostsService instance
    """
    global _posts_service
    if _posts_service is None:
        _posts_service = PostsService()
    return _posts_service

