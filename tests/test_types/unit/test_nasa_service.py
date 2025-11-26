"""
Unit tests for NASA API service.
Following TDD: tests are written first, implementation comes later.

These tests mock the external NASA API using the NASA mock infrastructure
to ensure consistent test data.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import HTTPStatusError

from app.schemas.nasa import APOD
from tests.infrastructure.external_apis.nasa.mock import NASAMock


@pytest.fixture
def nasa_mock():
    """Fixture that provides NASAMock instance for loading payloads"""
    return NASAMock()


@pytest.fixture
def mock_nasa_api(nasa_mock):
    """
    Fixture that mocks the external NASA API.
    Returns mock responses based on payloads loaded from infrastructure/external_apis/nasa/payloads/
    """
    # Patch httpx.AsyncClient directly since nasa_service doesn't exist yet (TDD)
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_client)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_context_manager
        
        # Configure mock responses based on payloads
        async def mock_get(url, **kwargs):
            mock_response = MagicMock()
            
            if "/planetary/apod" in url:
                # GET APOD
                data = nasa_mock.get_apod()
                mock_response.status_code = 200
                mock_response.json = MagicMock(return_value=data)
                mock_response.raise_for_status = MagicMock()
            else:
                # Unknown endpoint
                error_data = nasa_mock.get_apod_error()
                mock_response.status_code = 400
                mock_response.json = MagicMock(return_value=error_data)
                mock_response.raise_for_status = MagicMock(
                    side_effect=HTTPStatusError(
                        "400 Bad Request",
                        request=MagicMock(),
                        response=MagicMock(status_code=400)
                    )
                )
            
            return mock_response
        
        mock_client.get = AsyncMock(side_effect=mock_get)
        
        yield mock_client


@pytest.mark.asyncio
async def test_get_apod_success(mock_nasa_api, nasa_mock):
    """
    Test that NASAService can successfully retrieve APOD data.
    
    This test follows TDD - the service doesn't exist yet, so this will fail initially.
    """
    from app.services.nasa_service import NASAService
    
    service = NASAService(base_url="https://api.nasa.gov", api_key="test_key")
    apod = await service.get_apod()
    
    # Verify the response is an APOD object
    assert isinstance(apod, APOD)
    
    # Verify the data matches what we expect from the mock
    expected_data = nasa_mock.get_apod()
    assert apod.date == expected_data["date"]
    assert apod.title == expected_data["title"]
    assert apod.explanation == expected_data["explanation"]
    assert apod.media_type == expected_data["media_type"]
    assert apod.service_version == expected_data["service_version"]
    assert str(apod.url) == expected_data["url"]
    
    # Verify the API was called correctly
    mock_nasa_api.get.assert_called_once()
    call_args = mock_nasa_api.get.call_args
    assert "/planetary/apod" in call_args[0][0]
    assert "api_key" in call_args[1]["params"]


@pytest.mark.asyncio
async def test_get_apod_with_date_parameter(mock_nasa_api, nasa_mock):
    """
    Test that NASAService can retrieve APOD for a specific date.
    """
    from app.services.nasa_service import NASAService
    
    service = NASAService(base_url="https://api.nasa.gov", api_key="test_key")
    test_date = "2020-01-01"
    apod = await service.get_apod(date=test_date)
    
    # Verify the response is an APOD object
    assert isinstance(apod, APOD)
    assert apod.date == test_date
    
    # Verify the date parameter was passed to the API
    mock_nasa_api.get.assert_called_once()
    call_args = mock_nasa_api.get.call_args
    assert "date" in call_args[1]["params"]
    assert call_args[1]["params"]["date"] == test_date


@pytest.mark.asyncio
async def test_get_apod_with_hd_parameter(mock_nasa_api, nasa_mock):
    """
    Test that NASAService can request HD image URL.
    """
    from app.services.nasa_service import NASAService
    
    service = NASAService(base_url="https://api.nasa.gov", api_key="test_key")
    apod = await service.get_apod(hd=True)
    
    # Verify the response is an APOD object
    assert isinstance(apod, APOD)
    
    # Verify the hd parameter was passed to the API
    mock_nasa_api.get.assert_called_once()
    call_args = mock_nasa_api.get.call_args
    assert "hd" in call_args[1]["params"]
    assert call_args[1]["params"]["hd"] is True


@pytest.mark.asyncio
async def test_get_apod_api_error(mock_nasa_api, nasa_mock):
    """
    Test that NASAService properly handles API errors (400 Bad Request).
    """
    from app.services.nasa_service import NASAService
    
    # Configure mock to return error
    async def mock_get_error(url, **kwargs):
        mock_response = MagicMock()
        error_data = nasa_mock.get_apod_error()
        mock_response.status_code = 400
        mock_response.json = MagicMock(return_value=error_data)
        mock_response.raise_for_status = MagicMock(
            side_effect=HTTPStatusError(
                "400 Bad Request",
                request=MagicMock(),
                response=MagicMock(status_code=400)
            )
        )
        return mock_response
    
    mock_nasa_api.get = AsyncMock(side_effect=mock_get_error)
    
    service = NASAService(base_url="https://api.nasa.gov", api_key="test_key")
    
    # Verify that HTTPStatusError is raised
    with pytest.raises(HTTPStatusError) as exc_info:
        await service.get_apod()
    
    assert exc_info.value.response.status_code == 400

