"""
Dependency injection functions for NASA use cases.

These functions provide instances of use cases with their dependencies configured.
Following Clean Architecture: dependencies are injected at the application boundary.
"""
import os
from typing import Optional

from app.application.nasa.use_cases import GetAPODUseCase
from app.infrastructure.nasa.http_repository import NASAHTTPRepository


def get_apod_use_case() -> GetAPODUseCase:
    """
    Get GetAPODUseCase instance with repository dependency injected.
    
    Reads configuration from environment variables:
    - NASA_API_BASE_URL: Base URL for NASA API (default: https://api.nasa.gov)
    - NASA_API_KEY: NASA API key (default: empty string, uses demo key)
    
    Returns:
        GetAPODUseCase instance configured with HTTP repository
    """
    base_url = os.getenv("NASA_API_BASE_URL", "https://api.nasa.gov")
    api_key = os.getenv("NASA_API_KEY", "")
    
    repository = NASAHTTPRepository(base_url=base_url, api_key=api_key)
    return GetAPODUseCase(repository=repository)

