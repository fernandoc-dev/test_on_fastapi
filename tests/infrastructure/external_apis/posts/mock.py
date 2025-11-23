"""
Mock for Posts API provider for tests.
Loads payloads based on OpenAPI specification mapping.
"""
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

from .spec_loader import OpenAPISpecLoader


class PostsMock:
    """
    Mock for Posts API service.
    
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
    
    def _get_payload(self, method: str, path: str, status_code: str = "200", **path_params: Any) -> Optional[Dict[str, Any]]:
        """
        Get payload for an endpoint from OpenAPI spec mapping.
        
        Args:
            method: HTTP method
            path: API path (may contain {param} placeholders)
            status_code: HTTP status code
            **path_params: Path parameters to replace in payload filename (e.g., id=1)
            
        Returns:
            Payload data or None if not found
        """
        payload_path = self.spec_loader.get_payload_path(method, path, status_code)
        if payload_path:
            # Replace path parameters in filename if provided
            if path_params and "{id}" in str(payload_path):
                # Try specific ID file first
                specific_path = Path(str(payload_path).replace("{id}", str(path_params.get("id", ""))))
                if specific_path.exists():
                    return self._load_json_file(specific_path)
                # Fallback: try to find any matching file pattern
                pattern = str(payload_path).replace("{id}", "*")
                matching_files = list(self.payloads_dir.glob(pattern.replace("payloads/", "")))
                if matching_files:
                    return self._load_json_file(matching_files[0])
            
            if payload_path.exists():
                return self._load_json_file(payload_path)
        return None
    
    def get_all_posts(self) -> List[Dict[str, Any]]:
        """Returns list of all posts from OpenAPI-mapped payload"""
        payload = self._get_payload("GET", "/posts", "200")
        if payload is None:
            raise FileNotFoundError("Payload not found for GET /posts 200")
        return payload
    
    def get_post_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        """
        Returns post by ID from OpenAPI-mapped payload.
        
        Args:
            post_id: Post ID to retrieve
            
        Returns:
            Post data if found, None otherwise
        """
        # Try to get specific post payload (e.g., GET_posts_1_200.json)
        payload_path = self.payloads_dir / f"GET_posts_{post_id}_200.json"
        if payload_path.exists():
            return self._load_json_file(payload_path)
        
        # Only use generic template for IDs that are likely to exist (1, 2, etc.)
        # For high IDs like 999, return None to indicate not found
        if post_id > 100:
            return None
        
        # Fallback: try to load generic pattern and update ID
        # Look for any GET_posts_*_200.json file as template (but only for low IDs)
        generic_files = list(self.payloads_dir.glob("GET_posts_*_200.json"))
        if generic_files:
            payload = self._load_json_file(generic_files[0])
            payload = payload.copy()
            payload["id"] = post_id
            return payload
        
        return None
    
    def get_create_request(self) -> Dict[str, Any]:
        """Returns example post creation request from OpenAPI-mapped payload"""
        payload_path = self.spec_loader.get_request_payload_path("POST", "/posts")
        if payload_path:
            return self._load_json_file(payload_path)
        raise FileNotFoundError("Request payload not found for POST /posts")
    
    def get_create_response(self) -> Dict[str, Any]:
        """Returns example post creation response from OpenAPI-mapped payload"""
        payload = self._get_payload("POST", "/posts", "201")
        if payload is None:
            raise FileNotFoundError("Payload not found for POST /posts 201")
        return payload
    
    def get_update_request(self) -> Dict[str, Any]:
        """Returns example post update request from OpenAPI-mapped payload"""
        # Try specific ID first
        payload_path = self.payloads_dir / "PUT_posts_1_request.json"
        if payload_path.exists():
            return self._load_json_file(payload_path)
        
        # Fallback to generic
        payload_path = self.spec_loader.get_request_payload_path("PUT", "/posts/{id}")
        if payload_path:
            return self._load_json_file(payload_path)
        raise FileNotFoundError("Request payload not found for PUT /posts/{id}")
    
    def get_update_response(self) -> Dict[str, Any]:
        """Returns example post update response from OpenAPI-mapped payload"""
        # Try specific ID first
        payload_path = self.payloads_dir / "PUT_posts_1_200.json"
        if payload_path.exists():
            return self._load_json_file(payload_path)
        
        # Fallback to generic
        payload = self._get_payload("PUT", "/posts/{id}", "200")
        if payload is None:
            raise FileNotFoundError("Payload not found for PUT /posts/{id} 200")
        return payload
    
    def get_not_found_error(self, post_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Returns 404 error response from OpenAPI-mapped payload.
        
        Args:
            post_id: Optional post ID for specific error messages
            
        Returns:
            404 error payload
        """
        # Try specific ID first
        if post_id is not None:
            payload_path = self.payloads_dir / f"GET_posts_{post_id}_404.json"
            if payload_path.exists():
                return self._load_json_file(payload_path)
        
        # Try generic 404 from spec with path parameter
        payload = self._get_payload("GET", "/posts/{id}", "404", id=post_id or 999)
        if payload:
            # Update message with specific ID if provided
            if post_id is not None:
                payload = payload.copy()
                message = payload.get("message", "Not Found")
                # Replace any ID references in message
                payload["message"] = message.replace("999", str(post_id)).replace("{id}", str(post_id))
            return payload
        
        # Fallback to any 404 file
        error_files = list(self.payloads_dir.glob("*_404.json"))
        if error_files:
            payload = self._load_json_file(error_files[0])
            if post_id is not None:
                payload = payload.copy()
                message = payload.get("message", "Not Found")
                payload["message"] = message.replace("999", str(post_id)).replace("{id}", str(post_id))
            return payload
        
        return {
            "error": "Not Found",
            "message": f"Post with id {post_id} not found" if post_id else "Resource not found",
            "statusCode": 404
        }

