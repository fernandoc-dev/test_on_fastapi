"""
User domain entity
"""
import re
from app.domain.exceptions import InvalidEmailError


class User:
    """
    User domain entity.
    
    This is a domain entity - it contains business logic and validation rules.
    It doesn't know about databases, APIs, or frameworks.
    """
    
    # Email validation regex (simple version for now)
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self, email: str, username: str, is_active: bool = True):
        """
        Create a new User.
        
        Args:
            email: User's email address (must be valid)
            username: User's username
            is_active: Whether the user is active (default: True)
            
        Raises:
            InvalidEmailError: If the email is not valid
        """
        # Validate email
        if not self._is_valid_email(email):
            raise InvalidEmailError(f"Invalid email format: {email}")
        
        self.email = email
        self.username = username
        self.is_active = is_active
    
    @classmethod
    def _is_valid_email(cls, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email is valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        return bool(cls.EMAIL_REGEX.match(email))

