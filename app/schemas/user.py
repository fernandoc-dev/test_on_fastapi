"""
User schema - defines the structure of User objects in API responses
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class User(BaseModel):
    """
    User model for API responses.
    
    This is the target model - what we expect to receive from the API.
    """
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}  # Allows conversion from SQLAlchemy models

