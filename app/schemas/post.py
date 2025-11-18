"""
Post schema - defines the structure of Post objects in API responses and requests
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Post(BaseModel):
    """
    Post model for API responses.
    
    This is the target model - what we expect to receive from the external API.
    """
    id: int
    title: str
    body: str
    userId: int
    createdAt: str  # ISO 8601 datetime string
    updatedAt: Optional[str] = None  # ISO 8601 datetime string
    
    model_config = {"from_attributes": True}


class PostCreate(BaseModel):
    """
    Post creation request model.
    """
    title: str
    body: str
    userId: int


class PostUpdate(BaseModel):
    """
    Post update request model.
    All fields are optional for partial updates.
    """
    title: Optional[str] = None
    body: Optional[str] = None

