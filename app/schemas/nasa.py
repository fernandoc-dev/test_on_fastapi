"""
NASA API schemas - defines the structure of NASA API responses
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any


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


class NeoFeed(BaseModel):
    """
    Near Earth Object Feed model.
    """
    links: Dict[str, Optional[HttpUrl]]
    element_count: int
    near_earth_objects: Dict[str, List[Dict[str, Any]]]
    
    model_config = {"from_attributes": True}


class DonkiNotification(BaseModel):
    """
    Space Weather Notification (DONKI) model.
    """
    messageType: str
    messageID: str
    messageURL: HttpUrl
    messageIssueTime: str
    messageBody: str
    
    model_config = {"from_attributes": True}


class InsightWeather(BaseModel):
    """
    Mars Weather Service (InSight) model.
    """
    sol_keys: Optional[List[str]] = None
    validity_checks: Optional[Dict[str, Any]] = None
    description: Optional[Dict[str, Any]] = None
    
    model_config = {"from_attributes": True}


class TechTransferPatent(BaseModel):
    """
    Tech Transfer Patent model.
    """
    id: int
    title: str
    abstract: str
    patentNumber: str
    expirationDate: str
    applicationDate: str
    
    model_config = {"from_attributes": True}


class TechTransferPatents(BaseModel):
    """
    Tech Transfer Patents response model.
    """
    results: List[TechTransferPatent]
    
    model_config = {"from_attributes": True}

