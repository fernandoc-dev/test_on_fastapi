"""
Unit tests for User domain entity
"""
import pytest
from app.domain.entities.user import User
from app.domain.exceptions import InvalidEmailError


class TestUserEntity:
    """Test User domain entity"""
    
    def test_create_user_with_valid_email(self):
        """
        Test that we can create a user with a valid email address.
        
        This is our first test - it defines what we want:
        - A User entity that can be created
        - It must accept an email
        - The email must be valid
        """
        # Arrange: Prepare test data
        email = "user@example.com"
        username = "testuser"
        
        # Act: Create the user (this will fail initially - that's expected!)
        user = User(email=email, username=username)
        
        # Assert: Verify the user was created correctly
        assert user.email == email
        assert user.username == username
        assert user.is_active is True  # Default value
    
    def test_create_user_with_invalid_email_raises_error(self):
        """
        Test that creating a user with an invalid email raises an error.
        
        This test ensures our User entity validates email format.
        """
        # Arrange
        invalid_email = "not-an-email"
        username = "testuser"
        
        # Act & Assert: Verify that invalid email raises an error
        with pytest.raises(InvalidEmailError):
            User(email=invalid_email, username=username)

