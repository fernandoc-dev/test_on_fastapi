"""
User CRUD endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from app.database.connection import get_db
from app.database.models import UserModel
from app.schemas.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[User], status_code=status.HTTP_200_OK)
async def get_users(db: Session = Depends(get_db)):
    """
    Get all users.
    
    Returns:
        List of all users in the database
    """
    result = db.execute(select(UserModel))
    users = result.scalars().all()
    return [User.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        User object
        
    Raises:
        HTTPException: 404 if user not found
    """
    result = db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return User.model_validate(user)

