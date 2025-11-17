"""
User schema - defines the structure of User objects in API responses and requests
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


class UserCreate(BaseModel):
    """
    User creation request model.
    """
    email: EmailStr
    username: str
    is_active: bool = True


class UserUpdate(BaseModel):
    """
    User update request model.
    All fields are optional for partial updates.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None

