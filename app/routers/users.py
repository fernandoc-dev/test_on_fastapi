"""
User CRUD endpoints
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database.connection import get_db
from app.database.models import UserModel
from app.schemas.user import User, UserCreate, UserUpdate

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


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    Args:
        user_data: User creation data
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: 409 if email or username already exists
    """
    # Check if email already exists
    existing_email = db.execute(
        select(UserModel).where(UserModel.email == user_data.email)
    ).scalar_one_or_none()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {user_data.email} already exists"
        )
    
    # Check if username already exists
    existing_username = db.execute(
        select(UserModel).where(UserModel.username == user_data.username)
    ).scalar_one_or_none()
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username {user_data.username} already exists"
        )
    
    # Create new user
    new_user = UserModel(
        email=user_data.email,
        username=user_data.username,
        is_active=user_data.is_active,
        created_at=datetime.now(),
        updated_at=None
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return User.model_validate(new_user)


@router.put("/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a user by ID.
    
    Args:
        user_id: User ID
        user_data: User update data (partial update supported)
        
    Returns:
        Updated user object
        
    Raises:
        HTTPException: 404 if user not found, 409 if email/username conflict
    """
    # Get existing user
    result = db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Check email uniqueness if email is being updated
    if user_data.email is not None and user_data.email != user.email:
        existing_email = db.execute(
            select(UserModel).where(UserModel.email == user_data.email)
        ).scalar_one_or_none()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user_data.email} already exists"
            )
        user.email = user_data.email
    
    # Check username uniqueness if username is being updated
    if user_data.username is not None and user_data.username != user.username:
        existing_username = db.execute(
            select(UserModel).where(UserModel.username == user_data.username)
        ).scalar_one_or_none()
        
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with username {user_data.username} already exists"
            )
        user.username = user_data.username
    
    # Update other fields
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    # Update timestamp
    user.updated_at = datetime.now()
    
    db.commit()
    db.refresh(user)
    
    return User.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID.
    
    Args:
        user_id: User ID
        
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
    
    db.delete(user)
    db.commit()
    
    return None

