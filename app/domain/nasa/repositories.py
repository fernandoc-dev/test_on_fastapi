"""
NASA Repository Interface (Domain Layer).

This defines the contract that any NASA data source must implement.
Following Clean Architecture: domain layer doesn't depend on infrastructure.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from app.schemas.nasa import (
    APOD, NeoFeed, DonkiNotification, InsightWeather, TechTransferPatents
)


class NASARepository(ABC):
    """
    Abstract repository interface for NASA API data access.
    
    This interface defines what operations are available, not how they're implemented.
    Implementations can use HTTP, cache, database, etc.
    """
    
    @abstractmethod
    async def get_apod(self, date: Optional[str] = None, hd: bool = False) -> APOD:
        """
        Get Astronomy Picture of the Day (APOD).
        
        Args:
            date: Optional date in YYYY-MM-DD format
            hd: Whether to return HD image URL
            
        Returns:
            APOD object
        """
        pass
    
    @abstractmethod
    async def get_neo_feed(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        detailed: bool = False
    ) -> NeoFeed:
        """
        Get Near Earth Object Feed.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            detailed: Whether to return detailed information
            
        Returns:
            NeoFeed object
        """
        pass
    
    @abstractmethod
    async def get_donki_notifications(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        notification_type: Optional[str] = None
    ) -> List[DonkiNotification]:
        """
        Get Space Weather Notifications (DONKI).
        
        Args:
            start_date: Optional start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            notification_type: Optional event type (FLR, SEP, CME, GST, RBE, report)
            
        Returns:
            List of DonkiNotification objects
        """
        pass
    
    @abstractmethod
    async def get_insight_weather(
        self,
        feedtype: str = "json",
        ver: str = "1.0"
    ) -> InsightWeather:
        """
        Get Mars Weather Service (InSight) data.
        
        Args:
            feedtype: Response format (json or xml)
            ver: API version
            
        Returns:
            InsightWeather object
        """
        pass
    
    @abstractmethod
    async def get_techtransfer_patents(
        self,
        query: Optional[str] = None,
        limit: int = 10
    ) -> TechTransferPatents:
        """
        Get Tech Transfer Patents.
        
        Args:
            query: Optional search query
            limit: Number of results to return
            
        Returns:
            TechTransferPatents object
        """
        pass

