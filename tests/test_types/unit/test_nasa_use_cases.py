"""
Unit tests for NASA API use cases.
Following TDD: tests are written first, implementation comes later.

These tests verify the business logic in use cases, independent of HTTP implementation.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from typing import Optional

from app.schemas.nasa import (
    APOD, NeoFeed, DonkiNotification, InsightWeather, TechTransferPatents
)


# Tests for GetAPODUseCase
@pytest.mark.asyncio
async def test_get_apod_use_case_success():
    """
    Test that GetAPODUseCase successfully retrieves APOD data.
    TDD: Use case doesn't exist yet, this will fail initially.
    """
    from app.application.nasa.use_cases import GetAPODUseCase
    from app.domain.nasa.repositories import NASARepository
    
    # Mock repository
    mock_repository = Mock(spec=NASARepository)
    expected_apod = APOD(
        date="2020-01-01",
        explanation="Test explanation",
        title="Test Title",
        media_type="image",
        service_version="v1",
        url="https://example.com/image.jpg"
    )
    mock_repository.get_apod = AsyncMock(return_value=expected_apod)
    
    # Execute use case
    use_case = GetAPODUseCase(repository=mock_repository)
    result = await use_case.execute(date="2020-01-01", hd=False)
    
    # Verify result
    assert isinstance(result, APOD)
    assert result.date == "2020-01-01"
    assert result.title == "Test Title"
    
    # Verify repository was called correctly
    mock_repository.get_apod.assert_called_once_with(date="2020-01-01", hd=False)


@pytest.mark.asyncio
async def test_get_apod_use_case_with_hd():
    """Test that GetAPODUseCase passes hd parameter correctly."""
    from app.application.nasa.use_cases import GetAPODUseCase
    from app.domain.nasa.repositories import NASARepository
    
    mock_repository = Mock(spec=NASARepository)
    mock_repository.get_apod = AsyncMock(return_value=APOD(
        date="2020-01-01",
        explanation="Test",
        title="Test",
        media_type="image",
        service_version="v1",
        url="https://example.com/image.jpg"
    ))
    
    use_case = GetAPODUseCase(repository=mock_repository)
    await use_case.execute(hd=True)
    
    mock_repository.get_apod.assert_called_once_with(date=None, hd=True)


# Tests for GetNeoFeedUseCase
@pytest.mark.asyncio
async def test_get_neo_feed_use_case_success():
    """
    Test that GetNeoFeedUseCase successfully retrieves NEO feed data.
    TDD: Use case doesn't exist yet, this will fail initially.
    """
    from app.application.nasa.use_cases import GetNeoFeedUseCase
    from app.domain.nasa.repositories import NASARepository
    
    mock_repository = Mock(spec=NASARepository)
    expected_feed = NeoFeed(
        links={"self": "https://example.com"},
        element_count=12,
        near_earth_objects={"2015-09-07": []}
    )
    mock_repository.get_neo_feed = AsyncMock(return_value=expected_feed)
    
    use_case = GetNeoFeedUseCase(repository=mock_repository)
    result = await use_case.execute(start_date="2015-09-07", end_date="2015-09-08")
    
    assert isinstance(result, NeoFeed)
    assert result.element_count == 12
    mock_repository.get_neo_feed.assert_called_once_with(
        start_date="2015-09-07",
        end_date="2015-09-08",
        detailed=False
    )


@pytest.mark.asyncio
async def test_get_neo_feed_use_case_with_detailed():
    """Test that GetNeoFeedUseCase passes detailed parameter correctly."""
    from app.application.nasa.use_cases import GetNeoFeedUseCase
    from app.domain.nasa.repositories import NASARepository
    
    mock_repository = Mock(spec=NASARepository)
    mock_repository.get_neo_feed = AsyncMock(return_value=NeoFeed(
        links={},
        element_count=0,
        near_earth_objects={}
    ))
    
    use_case = GetNeoFeedUseCase(repository=mock_repository)
    await use_case.execute(start_date="2015-09-07", detailed=True)
    
    mock_repository.get_neo_feed.assert_called_once_with(
        start_date="2015-09-07",
        end_date=None,
        detailed=True
    )


# Tests for GetDonkiNotificationsUseCase
@pytest.mark.asyncio
async def test_get_donki_notifications_use_case_success():
    """
    Test that GetDonkiNotificationsUseCase successfully retrieves DONKI notifications.
    TDD: Use case doesn't exist yet, this will fail initially.
    """
    from app.application.nasa.use_cases import GetDonkiNotificationsUseCase
    from app.domain.nasa.repositories import NASARepository
    
    mock_repository = Mock(spec=NASARepository)
    expected_notifications = [
        DonkiNotification(
            messageType="FLR",
            messageID="2019-08-06T00:00:00-FLR-001",
            messageURL="https://example.com",
            messageIssueTime="2019-08-06T00:00:00Z",
            messageBody="Test message"
        )
    ]
    mock_repository.get_donki_notifications = AsyncMock(return_value=expected_notifications)
    
    use_case = GetDonkiNotificationsUseCase(repository=mock_repository)
    result = await use_case.execute(
        start_date="2019-08-06",
        end_date="2019-08-06",
        notification_type="FLR"
    )
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], DonkiNotification)
    assert result[0].messageType == "FLR"
    mock_repository.get_donki_notifications.assert_called_once_with(
        start_date="2019-08-06",
        end_date="2019-08-06",
        notification_type="FLR"
    )


# Tests for GetInsightWeatherUseCase
@pytest.mark.asyncio
async def test_get_insight_weather_use_case_success():
    """
    Test that GetInsightWeatherUseCase successfully retrieves Mars weather data.
    TDD: Use case doesn't exist yet, this will fail initially.
    """
    from app.application.nasa.use_cases import GetInsightWeatherUseCase
    from app.domain.nasa.repositories import NASARepository
    
    mock_repository = Mock(spec=NASARepository)
    expected_weather = InsightWeather(
        sol_keys=["675", "676"],
        validity_checks={},
        description={}
    )
    mock_repository.get_insight_weather = AsyncMock(return_value=expected_weather)
    
    use_case = GetInsightWeatherUseCase(repository=mock_repository)
    result = await use_case.execute(feedtype="json", ver="1.0")
    
    assert isinstance(result, InsightWeather)
    assert result.sol_keys == ["675", "676"]
    mock_repository.get_insight_weather.assert_called_once_with(feedtype="json", ver="1.0")


# Tests for GetTechTransferPatentsUseCase
@pytest.mark.asyncio
async def test_get_techtransfer_patents_use_case_success():
    """
    Test that GetTechTransferPatentsUseCase successfully retrieves patents.
    TDD: Use case doesn't exist yet, this will fail initially.
    """
    from app.application.nasa.use_cases import GetTechTransferPatentsUseCase
    from app.domain.nasa.repositories import NASARepository
    
    from app.schemas.nasa import TechTransferPatent
    
    mock_repository = Mock(spec=NASARepository)
    expected_patents = TechTransferPatents(
        results=[
            TechTransferPatent(
                id=1,
                title="Test Patent",
                abstract="Test abstract",
                patentNumber="US12345678",
                expirationDate="2035-12-31",
                applicationDate="2010-01-15"
            )
        ]
    )
    mock_repository.get_techtransfer_patents = AsyncMock(return_value=expected_patents)
    
    use_case = GetTechTransferPatentsUseCase(repository=mock_repository)
    result = await use_case.execute(query="solar", limit=10)
    
    assert isinstance(result, TechTransferPatents)
    assert len(result.results) == 1
    mock_repository.get_techtransfer_patents.assert_called_once_with(query="solar", limit=10)

