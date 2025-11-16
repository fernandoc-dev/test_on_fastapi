"""
Project domain entity
"""
from datetime import datetime
from typing import Optional
from app.domain.entities.user import User
from app.domain.exceptions import InvalidProjectNameError


class Project:
    """
    Project domain entity.
    
    A project represents a collection of tasks that can come from multiple sources:
    - Local tasks (stored in database)
    - GitHub issues (from external API)
    - Trello cards (from external API)
    """
    
    def __init__(
        self,
        name: str,
        owner: User,
        description: Optional[str] = None,
        status: str = "pending"
    ):
        """
        Create a new Project.
        
        Args:
            name: Project name (required, cannot be empty)
            owner: User who owns the project
            description: Project description (optional)
            status: Project status (default: "pending")
            
        Raises:
            InvalidProjectNameError: If the name is invalid
        """
        # Validate name
        if not self._is_valid_name(name):
            raise InvalidProjectNameError(f"Invalid project name: {name}")
        
        self.name = name
        self.owner = owner
        self.description = description
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @classmethod
    def _is_valid_name(cls, name: str) -> bool:
        """
        Validate project name.
        
        A valid name must:
        - Not be None
        - Be a string
        - Not be empty or only whitespace
        
        Args:
            name: Project name to validate
            
        Returns:
            True if name is valid, False otherwise
        """
        if name is None:
            return False
        if not isinstance(name, str):
            return False
        if not name.strip():  # Empty or only whitespace
            return False
        return True

