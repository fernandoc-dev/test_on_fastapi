"""
NASA HTTP Repository (Infrastructure Layer).

This is the concrete implementation of NASARepository that uses HTTP to call the NASA API.
Following Clean Architecture: infrastructure implements domain interfaces.
"""
import httpx
from typing import Optional, List

from app.domain.nasa.repositories import NASARepository
from app.schemas.nasa import (
    APOD, NeoFeed, DonkiNotification, InsightWeather, TechTransferPatents, TechTransferPatent
)


class NASAHTTPRepository(NASARepository):
    """
    HTTP implementation of NASA Repository.
    
    This class makes actual HTTP calls to the NASA API using httpx.
    """
    
    def __init__(self, base_url: str = "https://api.nasa.gov", api_key: str = ""):
        """
        Initialize HTTP repository.
        
        Args:
            base_url: Base URL of the NASA API
            api_key: NASA API key
        """
        self.base_url = base_url
        self.api_key = api_key
    
    async def get_apod(self, date: Optional[str] = None, hd: bool = False) -> APOD:
        """
        Get Astronomy Picture of the Day (APOD) from NASA API.
        
        Args:
            date: Optional date in YYYY-MM-DD format
            hd: Whether to return HD image URL
            
        Returns:
            APOD object
            
        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        params = {"api_key": self.api_key}
        
        if date:
            params["date"] = date
        
        if hd:
            params["hd"] = True
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/planetary/apod",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return APOD(**data)
    
    async def get_neo_feed(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        detailed: bool = False
    ) -> NeoFeed:
        """
        Get Near Earth Object Feed from NASA API.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            detailed: Whether to return detailed information
            
        Returns:
            NeoFeed object
            
        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        params = {
            "api_key": self.api_key,
            "start_date": start_date
        }
        
        if end_date:
            params["end_date"] = end_date
        
        if detailed:
            params["detailed"] = True
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/neo/rest/v1/feed",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return NeoFeed(**data)
    
    async def get_donki_notifications(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        notification_type: Optional[str] = None
    ) -> List[DonkiNotification]:
        """
        Get Space Weather Notifications (DONKI) from NASA API.
        
        Args:
            start_date: Optional start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            notification_type: Optional event type (FLR, SEP, CME, GST, RBE, report)
            
        Returns:
            List of DonkiNotification objects
            
        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        params = {"api_key": self.api_key}
        
        if start_date:
            params["startDate"] = start_date
        
        if end_date:
            params["endDate"] = end_date
        
        if notification_type:
            params["type"] = notification_type
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/DONKI/notifications",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return [DonkiNotification(**notification) for notification in data]
    
    async def get_insight_weather(
        self,
        feedtype: str = "json",
        ver: str = "1.0"
    ) -> InsightWeather:
        """
        Get Mars Weather Service (InSight) data from NASA API.
        
        Args:
            feedtype: Response format (json or xml)
            ver: API version
            
        Returns:
            InsightWeather object
            
        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        params = {
            "api_key": self.api_key,
            "feedtype": feedtype,
            "ver": ver
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/insight_weather/",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return InsightWeather(**data)
    
    async def get_techtransfer_patents(
        self,
        query: Optional[str] = None,
        limit: int = 10
    ) -> TechTransferPatents:
        """
        Get Tech Transfer Patents from NASA API.
        
        Args:
            query: Optional search query
            limit: Number of results to return
            
        Returns:
            TechTransferPatents object
            
        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        params = {
            "api_key": self.api_key,
            "limit": limit
        }
        
        if query:
            params["query"] = query
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/techtransfer/patent/",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            # Convert results list to TechTransferPatent objects
            patents_data = data.get("results", [])
            patents = [TechTransferPatent(**patent) for patent in patents_data]
            
            return TechTransferPatents(results=patents)

