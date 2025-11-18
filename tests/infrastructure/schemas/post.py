"""
Post schema specification for tests.
This is an independent schema that represents the expected API contract.
Following TDD: test schema defines the contract, implementation must satisfy it.
"""
from pydantic import BaseModel
from typing import Optional


class PostSpec(BaseModel):
    """
    Post specification model for API responses.
    
    This is the target model - what we expect to receive from the external API.
    Tests validate that the app response satisfies this contract.
    """
    id: int
    title: str
    body: str
    userId: int
    createdAt: str  # ISO 8601 datetime string
    updatedAt: Optional[str] = None  # ISO 8601 datetime string
    
    model_config = {"from_attributes": True}


class PostCreateSpec(BaseModel):
    """
    Post creation request specification model.
    """
    title: str
    body: str
    userId: int


class PostUpdateSpec(BaseModel):
    """
    Post update request specification model.
    All fields are optional for partial updates.
    """
    title: Optional[str] = None
    body: Optional[str] = None

