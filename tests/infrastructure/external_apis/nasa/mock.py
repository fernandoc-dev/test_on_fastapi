"""
Mock for NASA API provider for tests.
Loads payloads based on OpenAPI specification mapping.
"""
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

from .spec_loader import OpenAPISpecLoader


class NASAMock:
    """
    Mock for NASA API service.
    
    Uses OpenAPI specification to map endpoints to payload files.
    This ensures mocks are aligned with API contract and makes it easy
    to maintain when API changes.
    """
    
    def __init__(self):
        """Initialize mock with OpenAPI spec loader"""
        self.base_dir = Path(__file__).parent
        self.spec_path = self.base_dir / "openapi.yaml"
        self.spec_loader = OpenAPISpecLoader(self.spec_path)
        self.payloads_dir = self.base_dir / "payloads"
    
    def _load_json_file(self, file_path: Path) -> Any:
        """
        Load JSON file from path.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Payload file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _get_payload(self, method: str, path: str, status_code: str = "200") -> Optional[Dict[str, Any]]:
        """
        Get payload for an endpoint from OpenAPI spec mapping.
        
        Args:
            method: HTTP method
            path: API path
            status_code: HTTP status code
            
        Returns:
            Payload data or None if not found
        """
        payload_path = self.spec_loader.get_payload_path(method, path, status_code)
        if payload_path and payload_path.exists():
            return self._load_json_file(payload_path)
        return None
    
    def get_apod(self, date: Optional[str] = None, hd: bool = False) -> Dict[str, Any]:
        """
        Returns Astronomy Picture of the Day (APOD) data.
        
        Args:
            date: Optional date in YYYY-MM-DD format
            hd: Whether to return HD URL
            
        Returns:
            APOD data
            
        Raises:
            FileNotFoundError: If payload not found
        """
        payload = self._get_payload("GET", "/planetary/apod", "200")
        if payload is None:
            raise FileNotFoundError("Payload not found for GET /planetary/apod 200")
        return payload
    
    def get_apod_error(self) -> Dict[str, Any]:
        """
        Returns 400 error response for APOD endpoint.
        
        Returns:
            400 error payload
        """
        payload = self._get_payload("GET", "/planetary/apod", "400")
        if payload is None:
            return {
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Invalid request parameters"
                }
            }
        return payload
    
    def get_neo_feed(self, start_date: str, end_date: Optional[str] = None, detailed: bool = False) -> Dict[str, Any]:
        """
        Returns Near Earth Object Feed data.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            detailed: Whether to return detailed information
            
        Returns:
            NEO feed data
            
        Raises:
            FileNotFoundError: If payload not found
        """
        payload = self._get_payload("GET", "/neo/rest/v1/feed", "200")
        if payload is None:
            raise FileNotFoundError("Payload not found for GET /neo/rest/v1/feed 200")
        return payload
    
    def get_neo_feed_error(self) -> Dict[str, Any]:
        """
        Returns 400 error response for NEO Feed endpoint.
        
        Returns:
            400 error payload
        """
        payload = self._get_payload("GET", "/neo/rest/v1/feed", "400")
        if payload is None:
            return {
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "start_date and end_date must be within 7 days of each other"
                }
            }
        return payload
    
    def get_donki_notifications(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        notification_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns Space Weather Notifications (DONKI) data.
        
        Args:
            start_date: Optional start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            notification_type: Optional event type (FLR, SEP, CME, GST, RBE, report)
            
        Returns:
            List of DONKI notifications
            
        Raises:
            FileNotFoundError: If payload not found
        """
        payload = self._get_payload("GET", "/DONKI/notifications", "200")
        if payload is None:
            raise FileNotFoundError("Payload not found for GET /DONKI/notifications 200")
        return payload
    
    def get_donki_notifications_error(self) -> Dict[str, Any]:
        """
        Returns 400 error response for DONKI Notifications endpoint.
        
        Returns:
            400 error payload
        """
        payload = self._get_payload("GET", "/DONKI/notifications", "400")
        if payload is None:
            return {
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Invalid date format. Use YYYY-MM-DD"
                }
            }
        return payload
    
    def get_insight_weather(self, feedtype: str = "json", ver: str = "1.0") -> Dict[str, Any]:
        """
        Returns Mars Weather Service (InSight) data.
        
        Args:
            feedtype: Response format (json or xml)
            ver: API version
            
        Returns:
            InSight weather data
            
        Raises:
            FileNotFoundError: If payload not found
        """
        payload = self._get_payload("GET", "/insight_weather/", "200")
        if payload is None:
            raise FileNotFoundError("Payload not found for GET /insight_weather/ 200")
        return payload
    
    def get_insight_weather_error(self) -> Dict[str, Any]:
        """
        Returns 400 error response for InSight Weather endpoint.
        
        Returns:
            400 error payload
        """
        payload = self._get_payload("GET", "/insight_weather/", "400")
        if payload is None:
            return {
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Invalid feedtype. Must be 'json' or 'xml'"
                }
            }
        return payload
    
    def get_techtransfer_patents(self, query: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Returns Tech Transfer Patents data.
        
        Args:
            query: Optional search query
            limit: Number of results to return (default: 10)
            
        Returns:
            Tech transfer patents data
            
        Raises:
            FileNotFoundError: If payload not found
        """
        payload = self._get_payload("GET", "/techtransfer/patent/", "200")
        if payload is None:
            raise FileNotFoundError("Payload not found for GET /techtransfer/patent/ 200")
        return payload
    
    def get_techtransfer_patents_error(self) -> Dict[str, Any]:
        """
        Returns 400 error response for Tech Transfer Patents endpoint.
        
        Returns:
            400 error payload
        """
        payload = self._get_payload("GET", "/techtransfer/patent/", "400")
        if payload is None:
            return {
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Invalid limit parameter. Must be between 1 and 100"
                }
            }
        return payload

