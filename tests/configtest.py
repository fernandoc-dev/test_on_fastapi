"""
Basic configuration for tests
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Test database configuration (if needed)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://test_user:test_pass@localhost:5432/test_db"
)

# API configuration
TEST_API_URL = os.getenv("TEST_API_URL", "http://localhost:8000")

# Pytest configuration
pytest_plugins = ["pytest_asyncio"]

