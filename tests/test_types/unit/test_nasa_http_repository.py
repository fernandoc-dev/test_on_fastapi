"""
Unit tests for NASA HTTP Repository.
Following TDD: tests are written first, implementation comes later.

These tests verify that the HTTP repository makes correct API calls.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import HTTPStatusError

from app.schemas.nasa import (
    APOD, NeoFeed, DonkiNotification, InsightWeather, TechTransferPatents
)
from tests.infrastructure.external_apis.nasa.mock import NASAMock


@pytest.fixture
def nasa_mock():
    """Fixture that provides NASAMock instance for loading payloads"""
    return NASAMock()


@pytest.fixture
def mock_http_client():
    """Fixture that mocks httpx.AsyncClient"""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_client)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_context_manager
        yield mock_client


@pytest.mark.asyncio
async def test_http_repository_get_apod(mock_http_client, nasa_mock):
    """
    Test that NASAHTTPRepository correctly calls APOD endpoint.
    TDD: Repository doesn't exist yet, this will fail initially.
    """
    from app.infrastructure.nasa.http_repository import NASAHTTPRepository
    
    # Setup mock response
    apod_data = nasa_mock.get_apod()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=apod_data)
    mock_response.raise_for_status = MagicMock()
    mock_http_client.get = AsyncMock(return_value=mock_response)
    
    # Execute
    repository = NASAHTTPRepository(base_url="https://api.nasa.gov", api_key="test_key")
    result = await repository.get_apod(date="2020-01-01", hd=False)
    
    # Verify result
    assert isinstance(result, APOD)
    assert result.date == apod_data["date"]
    assert result.title == apod_data["title"]
    
    # Verify HTTP call
    mock_http_client.get.assert_called_once()
    call_args = mock_http_client.get.call_args
    assert "/planetary/apod" in call_args[0][0]
    assert call_args[1]["params"]["api_key"] == "test_key"
    assert call_args[1]["params"]["date"] == "2020-01-01"
    # hd=False should not be included in params (only include if True)
    assert "hd" not in call_args[1]["params"]


@pytest.mark.asyncio
async def test_http_repository_get_neo_feed(mock_http_client, nasa_mock):
    """
    Test that NASAHTTPRepository correctly calls NEO Feed endpoint.
    TDD: Repository doesn't exist yet, this will fail initially.
    """
    from app.infrastructure.nasa.http_repository import NASAHTTPRepository
    
    neo_data = nasa_mock.get_neo_feed("2015-09-07")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=neo_data)
    mock_response.raise_for_status = MagicMock()
    mock_http_client.get = AsyncMock(return_value=mock_response)
    
    repository = NASAHTTPRepository(base_url="https://api.nasa.gov", api_key="test_key")
    result = await repository.get_neo_feed(start_date="2015-09-07", end_date="2015-09-08")
    
    assert isinstance(result, NeoFeed)
    assert result.element_count == neo_data["element_count"]
    
    call_args = mock_http_client.get.call_args
    assert "/neo/rest/v1/feed" in call_args[0][0]
    assert call_args[1]["params"]["start_date"] == "2015-09-07"
    assert call_args[1]["params"]["end_date"] == "2015-09-08"


@pytest.mark.asyncio
async def test_http_repository_get_donki_notifications(mock_http_client, nasa_mock):
    """
    Test that NASAHTTPRepository correctly calls DONKI Notifications endpoint.
    TDD: Repository doesn't exist yet, this will fail initially.
    """
    from app.infrastructure.nasa.http_repository import NASAHTTPRepository
    
    donki_data = nasa_mock.get_donki_notifications()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=donki_data)
    mock_response.raise_for_status = MagicMock()
    mock_http_client.get = AsyncMock(return_value=mock_response)
    
    repository = NASAHTTPRepository(base_url="https://api.nasa.gov", api_key="test_key")
    result = await repository.get_donki_notifications(
        start_date="2019-08-06",
        notification_type="FLR"
    )
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], DonkiNotification)
    
    call_args = mock_http_client.get.call_args
    assert "/DONKI/notifications" in call_args[0][0]
    assert call_args[1]["params"]["startDate"] == "2019-08-06"
    assert call_args[1]["params"]["type"] == "FLR"


@pytest.mark.asyncio
async def test_http_repository_get_insight_weather(mock_http_client, nasa_mock):
    """
    Test that NASAHTTPRepository correctly calls InSight Weather endpoint.
    TDD: Repository doesn't exist yet, this will fail initially.
    """
    from app.infrastructure.nasa.http_repository import NASAHTTPRepository
    
    weather_data = nasa_mock.get_insight_weather()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=weather_data)
    mock_response.raise_for_status = MagicMock()
    mock_http_client.get = AsyncMock(return_value=mock_response)
    
    repository = NASAHTTPRepository(base_url="https://api.nasa.gov", api_key="test_key")
    result = await repository.get_insight_weather(feedtype="json", ver="1.0")
    
    assert isinstance(result, InsightWeather)
    assert result.sol_keys is not None
    
    call_args = mock_http_client.get.call_args
    assert "/insight_weather/" in call_args[0][0]
    assert call_args[1]["params"]["feedtype"] == "json"
    assert call_args[1]["params"]["ver"] == "1.0"


@pytest.mark.asyncio
async def test_http_repository_get_techtransfer_patents(mock_http_client, nasa_mock):
    """
    Test that NASAHTTPRepository correctly calls Tech Transfer Patents endpoint.
    TDD: Repository doesn't exist yet, this will fail initially.
    """
    from app.infrastructure.nasa.http_repository import NASAHTTPRepository
    
    patents_data = nasa_mock.get_techtransfer_patents()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=patents_data)
    mock_response.raise_for_status = MagicMock()
    mock_http_client.get = AsyncMock(return_value=mock_response)
    
    repository = NASAHTTPRepository(base_url="https://api.nasa.gov", api_key="test_key")
    result = await repository.get_techtransfer_patents(query="solar", limit=10)
    
    assert isinstance(result, TechTransferPatents)
    assert len(result.results) > 0
    
    call_args = mock_http_client.get.call_args
    assert "/techtransfer/patent/" in call_args[0][0]
    assert call_args[1]["params"]["query"] == "solar"
    assert call_args[1]["params"]["limit"] == 10


@pytest.mark.asyncio
async def test_http_repository_handles_errors(mock_http_client):
    """Test that NASAHTTPRepository properly handles HTTP errors."""
    from app.infrastructure.nasa.http_repository import NASAHTTPRepository
    
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status = MagicMock(
        side_effect=HTTPStatusError(
            "400 Bad Request",
            request=MagicMock(),
            response=MagicMock(status_code=400)
        )
    )
    mock_http_client.get = AsyncMock(return_value=mock_response)
    
    repository = NASAHTTPRepository(base_url="https://api.nasa.gov", api_key="test_key")
    
    with pytest.raises(HTTPStatusError) as exc_info:
        await repository.get_apod()
    
    assert exc_info.value.response.status_code == 400

