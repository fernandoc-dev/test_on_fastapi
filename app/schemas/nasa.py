"""
NASA API schemas - defines the structure of NASA API responses
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional


class APOD(BaseModel):
    """
    Astronomy Picture of the Day (APOD) model.
    
    This is the target model - what we expect to receive from the NASA API.
    """
    date: str  # YYYY-MM-DD format
    explanation: str
    hdurl: Optional[HttpUrl] = None
    media_type: str  # "image" or "video"
    service_version: str
    title: str
    url: HttpUrl
    copyright: Optional[str] = None
    
    model_config = {"from_attributes": True}

