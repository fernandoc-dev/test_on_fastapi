"""
Unit tests for Project domain entity
"""
import pytest
from datetime import datetime
from app.domain.entities.user import User
from app.domain.entities.project import Project
from app.domain.exceptions import InvalidProjectNameError


class TestProjectEntity:
    """Test Project domain entity"""
    
    def test_create_project_with_valid_data(self):
        """
        Test that we can create a project with valid data.
        
        A project should have:
        - A name (required)
        - A description (optional)
        - An owner (User)
        - A status (default: 'pending')
        """
        # Arrange
        owner = User(email="owner@example.com", username="owner")
        project_name = "My First Project"
        description = "This is a test project"
        
        # Act
        project = Project(
            name=project_name,
            owner=owner,
            description=description
        )
        
        # Assert
        assert project.name == project_name
        assert project.description == description
        assert project.owner == owner
        assert project.status == "pending"  # Default status
        assert project.created_at is not None
        assert isinstance(project.created_at, datetime)
    
    def test_create_project_without_description(self):
        """
        Test that we can create a project without a description.
        Description should be optional.
        """
        # Arrange
        owner = User(email="owner@example.com", username="owner")
        project_name = "Simple Project"
        
        # Act
        project = Project(name=project_name, owner=owner)
        
        # Assert
        assert project.name == project_name
        assert project.description is None
        assert project.owner == owner
    
    def test_create_project_with_empty_name_raises_error(self):
        """
        Test that creating a project with an empty name raises an error.
        Project name is required and cannot be empty.
        """
        # Arrange
        owner = User(email="owner@example.com", username="owner")
        
        # Act & Assert
        with pytest.raises(InvalidProjectNameError):
            Project(name="", owner=owner)
        
        with pytest.raises(InvalidProjectNameError):
            Project(name="   ", owner=owner)  # Only whitespace
    
    def test_create_project_with_none_name_raises_error(self):
        """
        Test that creating a project with None as name raises an error.
        """
        # Arrange
        owner = User(email="owner@example.com", username="owner")
        
        # Act & Assert
        with pytest.raises(InvalidProjectNameError):
            Project(name=None, owner=owner)
    
    def test_project_can_change_status(self):
        """
        Test that a project can change its status.
        """
        # Arrange
        owner = User(email="owner@example.com", username="owner")
        project = Project(name="Test Project", owner=owner)
        
        # Act
        project.status = "active"
        
        # Assert
        assert project.status == "active"
        
        # Act
        project.status = "completed"
        
        # Assert
        assert project.status == "completed"

