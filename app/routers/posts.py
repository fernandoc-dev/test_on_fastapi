"""
Posts CRUD endpoints - proxy to external Posts API.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.post import Post, PostCreate, PostUpdate
from app.services.posts_service import get_posts_service, PostsService
import httpx


router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=List[Post], status_code=status.HTTP_200_OK)
async def get_posts(service: PostsService = Depends(get_posts_service)):
    """
    Get all posts from external API.
    
    Returns:
        List of all posts
        
    Raises:
        HTTPException: 500 if external API fails
    """
    try:
        posts = await service.get_all_posts()
        return posts
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching posts from external API: {str(e)}"
        )


@router.get("/{post_id}", response_model=Post, status_code=status.HTTP_200_OK)
async def get_post(
    post_id: int,
    service: PostsService = Depends(get_posts_service)
):
    """
    Get post by ID from external API.
    
    Args:
        post_id: Post ID
        
    Returns:
        Post object
        
    Raises:
        HTTPException: 404 if post not found, 500 if external API fails
    """
    try:
        post = await service.get_post_by_id(post_id)
        return post
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {post_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching post from external API: {str(e)}"
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching post from external API: {str(e)}"
        )


@router.post("", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    service: PostsService = Depends(get_posts_service)
):
    """
    Create a new post in external API.
    
    Args:
        post_data: Post creation data
        
    Returns:
        Created post object
        
    Raises:
        HTTPException: 500 if external API fails
    """
    try:
        post = await service.create_post(post_data)
        return post
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating post in external API: {str(e)}"
        )


@router.put("/{post_id}", response_model=Post, status_code=status.HTTP_200_OK)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    service: PostsService = Depends(get_posts_service)
):
    """
    Update a post in external API.
    
    Args:
        post_id: Post ID
        post_data: Post update data (partial update supported)
        
    Returns:
        Updated post object
        
    Raises:
        HTTPException: 404 if post not found, 500 if external API fails
    """
    try:
        post = await service.update_post(post_id, post_data)
        return post
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {post_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating post in external API: {str(e)}"
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating post in external API: {str(e)}"
        )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    service: PostsService = Depends(get_posts_service)
):
    """
    Delete a post from external API.
    
    Args:
        post_id: Post ID
        
    Raises:
        HTTPException: 404 if post not found, 500 if external API fails
    """
    try:
        await service.delete_post(post_id)
        return None
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {post_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting post from external API: {str(e)}"
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting post from external API: {str(e)}"
        )

