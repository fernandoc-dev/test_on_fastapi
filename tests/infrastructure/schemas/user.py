"""
User schema for tests - represents the expected API contract.

This is the specification model, independent from app.schemas.user.
Changes here represent new requirements that the app must satisfy.

Usage in tests:
    user = UserSpec(**response.json())  # Validates response matches spec
    assert user.email == expected_email  # Validate specific business logic
"""
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, Union


class UserSpec(BaseModel):
    """
    User specification model for tests.
    
    This model represents what the API should return according to requirements.
    It is independent from the app implementation to ensure tests validate
    that the app satisfies the requirements, not just internal consistency.
    
    When requirements change:
    1. Update this model first (add new fields, change types, etc.)
    2. Run tests - they will fail (RED phase)
    3. Update app implementation to satisfy the test (GREEN phase)
    4. Refactor if needed
    
    This model can be reused across:
    - Unit tests
    - Integration tests
    - E2E tests
    - Load tests
    """
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def parse_datetime(cls, v: Union[str, datetime]) -> datetime:
        """Parse datetime from string (JSON) or datetime object"""
        if isinstance(v, str):
            # FastAPI serializes datetime to ISO format string
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    
    model_config = {
        "from_attributes": True,  # Allows conversion from dict/ORM objects
    }


class UserCreateSpec(BaseModel):
    """
    User creation request specification for tests.
    
    Defines what the API should accept when creating a user.
    """
    email: EmailStr
    username: str
    is_active: bool = True


class UserUpdateSpec(BaseModel):
    """
    User update request specification for tests.
    
    Defines what the API should accept when updating a user.
    All fields are optional for partial updates.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
