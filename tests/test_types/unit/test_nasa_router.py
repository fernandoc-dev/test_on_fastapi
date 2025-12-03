"""
Unit tests for NASA router endpoints.

These tests verify the router layer, mocking the use case dependency.
Following TDD: tests are written first, implementation comes later.
"""
import pytest
from unittest.mock import AsyncMock, Mock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from httpx import HTTPStatusError

from app.schemas.nasa import APOD
from app.routers import nasa


@pytest.fixture
def mock_use_case():
    """Fixture that provides a mocked GetAPODUseCase"""
    mock = Mock()
    mock.execute = AsyncMock()
    return mock


@pytest.fixture
def app_with_nasa_router(mock_use_case):
    """Fixture that creates a FastAPI app with NASA router and mocked dependency"""
    from app.application.nasa.dependencies import get_apod_use_case
    
    # Create test app
    test_app = FastAPI()
    test_app.include_router(nasa.router)
    
    # Override dependency to return mock
    test_app.dependency_overrides[get_apod_use_case] = lambda: mock_use_case
    
    return test_app


@pytest.fixture
def client(app_with_nasa_router):
    """Fixture that provides a TestClient for the test app"""
    return TestClient(app_with_nasa_router)


@pytest.mark.asyncio
async def test_get_apod_success(client, mock_use_case):
    """
    Test that GET /nasa/apod successfully returns APOD data.
    
    Verifies:
    - Router calls use case with correct parameters
    - Response status is 200
    - Response body matches APOD schema
    """
    # Setup mock response
    expected_apod = APOD(
        date="2020-01-01",
        explanation="Test explanation",
        title="Test Title",
        media_type="image",
        service_version="v1",
        url="https://example.com/image.jpg"
    )
    mock_use_case.execute.return_value = expected_apod
    
    # Execute request
    response = client.get("/nasa/apod")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2020-01-01"
    assert data["title"] == "Test Title"
    assert data["explanation"] == "Test explanation"
    assert data["media_type"] == "image"
    assert data["service_version"] == "v1"
    assert data["url"] == "https://example.com/image.jpg"
    
    # Verify use case was called correctly
    mock_use_case.execute.assert_called_once_with(date=None, hd=False)


@pytest.mark.asyncio
async def test_get_apod_with_date_parameter(client, mock_use_case):
    """
    Test that GET /nasa/apod accepts date query parameter.
    
    Verifies:
    - Router passes date parameter to use case
    - Response is correct
    """
    expected_apod = APOD(
        date="2020-01-01",
        explanation="Test",
        title="Test",
        media_type="image",
        service_version="v1",
        url="https://example.com/image.jpg"
    )
    mock_use_case.execute.return_value = expected_apod
    
    response = client.get("/nasa/apod?date=2020-01-01")
    
    assert response.status_code == 200
    mock_use_case.execute.assert_called_once_with(date="2020-01-01", hd=False)


@pytest.mark.asyncio
async def test_get_apod_with_hd_parameter(client, mock_use_case):
    """
    Test that GET /nasa/apod accepts hd query parameter.
    
    Verifies:
    - Router passes hd parameter to use case
    - Response is correct
    """
    expected_apod = APOD(
        date="2020-01-01",
        explanation="Test",
        title="Test",
        media_type="image",
        service_version="v1",
        url="https://example.com/image.jpg",
        hdurl="https://example.com/image_hd.jpg"
    )
    mock_use_case.execute.return_value = expected_apod
    
    response = client.get("/nasa/apod?hd=true")
    
    assert response.status_code == 200
    mock_use_case.execute.assert_called_once_with(date=None, hd=True)


@pytest.mark.asyncio
async def test_get_apod_with_all_parameters(client, mock_use_case):
    """
    Test that GET /nasa/apod accepts both date and hd parameters.
    
    Verifies:
    - Router passes both parameters to use case
    - Response is correct
    """
    expected_apod = APOD(
        date="2020-01-01",
        explanation="Test",
        title="Test",
        media_type="image",
        service_version="v1",
        url="https://example.com/image.jpg"
    )
    mock_use_case.execute.return_value = expected_apod
    
    response = client.get("/nasa/apod?date=2020-01-01&hd=true")
    
    assert response.status_code == 200
    mock_use_case.execute.assert_called_once_with(date="2020-01-01", hd=True)


@pytest.mark.asyncio
async def test_get_apod_handles_http_status_error_400(client, mock_use_case):
    """
    Test that GET /nasa/apod handles 400 Bad Request from use case.
    
    Verifies:
    - Router converts HTTPStatusError 400 to HTTPException 400
    - Error message is appropriate
    """
    # Setup mock to raise HTTPStatusError
    mock_response = Mock()
    mock_response.status_code = 400
    error = HTTPStatusError(
        "400 Bad Request",
        request=Mock(),
        response=mock_response
    )
    mock_use_case.execute.side_effect = error
    
    response = client.get("/nasa/apod")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid request" in data["detail"] or "400" in data["detail"]


@pytest.mark.asyncio
async def test_get_apod_handles_http_status_error_500(client, mock_use_case):
    """
    Test that GET /nasa/apod handles 500 Internal Server Error from use case.
    
    Verifies:
    - Router converts HTTPStatusError 500 to HTTPException 500
    - Error message is appropriate
    """
    # Setup mock to raise HTTPStatusError
    mock_response = Mock()
    mock_response.status_code = 500
    error = HTTPStatusError(
        "500 Internal Server Error",
        request=Mock(),
        response=mock_response
    )
    mock_use_case.execute.side_effect = error
    
    response = client.get("/nasa/apod")
    
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Error fetching APOD" in data["detail"] or "500" in data["detail"]


@pytest.mark.asyncio
async def test_get_apod_handles_http_error(client, mock_use_case):
    """
    Test that GET /nasa/apod handles generic HTTPError from use case.
    
    Verifies:
    - Router converts HTTPError to HTTPException 500
    - Error message is appropriate
    """
    from httpx import HTTPError
    
    # Setup mock to raise HTTPError
    mock_use_case.execute.side_effect = HTTPError("Connection error")
    
    response = client.get("/nasa/apod")
    
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Error connecting" in data["detail"] or "Connection error" in data["detail"]

