"""
NASA API service - handles communication with external NASA API.
"""
import httpx
from typing import Optional
from app.schemas.nasa import APOD


class NASAService:
    """Service for interacting with external NASA API"""
    
    def __init__(self, base_url: str = "https://api.nasa.gov", api_key: str = ""):
        """
        Initialize NASA service.
        
        Args:
            base_url: Base URL of the NASA API
            api_key: NASA API key
        """
        self.base_url = base_url
        self.api_key = api_key
        self.apod_endpoint = f"{base_url}/planetary/apod"
    
    async def get_apod(self, date: Optional[str] = None, hd: bool = False) -> APOD:
        """
        Get Astronomy Picture of the Day (APOD) from NASA API.
        
        Args:
            date: Optional date in YYYY-MM-DD format. Defaults to today.
            hd: Whether to return HD image URL. Defaults to False.
            
        Returns:
            APOD object
            
        Raises:
            httpx.HTTPStatusError: If API request fails (400, 404, etc.)
        """
        params = {
            "api_key": self.api_key
        }
        
        if date:
            params["date"] = date
        
        if hd:
            params["hd"] = True
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.apod_endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            return APOD(**data)

