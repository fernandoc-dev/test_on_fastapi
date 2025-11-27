"""
NASA API Use Cases (Application Layer).

These use cases contain business logic and orchestrate calls to the repository.
Following Clean Architecture: application layer depends on domain interfaces, not implementations.
"""
from typing import Optional, List

from app.domain.nasa.repositories import NASARepository
from app.schemas.nasa import (
    APOD, NeoFeed, DonkiNotification, InsightWeather, TechTransferPatents
)


class GetAPODUseCase:
    """
    Use case for retrieving Astronomy Picture of the Day (APOD).
    
    This use case orchestrates the retrieval of APOD data from the repository.
    Business logic can be added here (e.g., caching, validation, transformation).
    """
    
    def __init__(self, repository: NASARepository):
        """
        Initialize use case with repository.
        
        Args:
            repository: NASA repository implementation (dependency injection)
        """
        self.repository = repository
    
    async def execute(self, date: Optional[str] = None, hd: bool = False) -> APOD:
        """
        Execute the use case: get APOD data.
        
        Args:
            date: Optional date in YYYY-MM-DD format
            hd: Whether to return HD image URL
            
        Returns:
            APOD object
            
        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        return await self.repository.get_apod(date=date, hd=hd)


class GetNeoFeedUseCase:
    """
    Use case for retrieving Near Earth Object Feed.
    """
    
    def __init__(self, repository: NASARepository):
        """Initialize use case with repository."""
        self.repository = repository
    
    async def execute(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        detailed: bool = False
    ) -> NeoFeed:
        """
        Execute the use case: get NEO feed data.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            detailed: Whether to return detailed information
            
        Returns:
            NeoFeed object
        """
        return await self.repository.get_neo_feed(
            start_date=start_date,
            end_date=end_date,
            detailed=detailed
        )


class GetDonkiNotificationsUseCase:
    """
    Use case for retrieving Space Weather Notifications (DONKI).
    """
    
    def __init__(self, repository: NASARepository):
        """Initialize use case with repository."""
        self.repository = repository
    
    async def execute(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        notification_type: Optional[str] = None
    ) -> List[DonkiNotification]:
        """
        Execute the use case: get DONKI notifications.
        
        Args:
            start_date: Optional start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            notification_type: Optional event type (FLR, SEP, CME, GST, RBE, report)
            
        Returns:
            List of DonkiNotification objects
        """
        return await self.repository.get_donki_notifications(
            start_date=start_date,
            end_date=end_date,
            notification_type=notification_type
        )


class GetInsightWeatherUseCase:
    """
    Use case for retrieving Mars Weather Service (InSight) data.
    """
    
    def __init__(self, repository: NASARepository):
        """Initialize use case with repository."""
        self.repository = repository
    
    async def execute(self, feedtype: str = "json", ver: str = "1.0") -> InsightWeather:
        """
        Execute the use case: get InSight weather data.
        
        Args:
            feedtype: Response format (json or xml)
            ver: API version
            
        Returns:
            InsightWeather object
        """
        return await self.repository.get_insight_weather(feedtype=feedtype, ver=ver)


class GetTechTransferPatentsUseCase:
    """
    Use case for retrieving Tech Transfer Patents.
    """
    
    def __init__(self, repository: NASARepository):
        """Initialize use case with repository."""
        self.repository = repository
    
    async def execute(
        self,
        query: Optional[str] = None,
        limit: int = 10
    ) -> TechTransferPatents:
        """
        Execute the use case: get tech transfer patents.
        
        Args:
            query: Optional search query
            limit: Number of results to return
            
        Returns:
            TechTransferPatents object
        """
        return await self.repository.get_techtransfer_patents(query=query, limit=limit)

