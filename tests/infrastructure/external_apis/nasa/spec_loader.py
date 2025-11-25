"""
OpenAPI specification loader for NASA API.
Maps endpoints to payload files based on OpenAPI spec.
"""
from typing import Dict, Optional, Any
import yaml
from pathlib import Path


class OpenAPISpecLoader:
    """Loads OpenAPI spec and maps endpoints to payload files"""
    
    def __init__(self, spec_path: Path):
        """
        Initialize spec loader.
        
        Args:
            spec_path: Path to OpenAPI YAML file
        """
        self.spec_path = spec_path
        self.spec_dir = spec_path.parent
        self._spec: Optional[Dict[str, Any]] = None
        self._endpoint_map: Optional[Dict[str, str]] = None
    
    def _load_spec(self) -> Dict[str, Any]:
        """Load and cache OpenAPI spec"""
        if self._spec is None:
            with open(self.spec_path, "r", encoding="utf-8") as f:
                self._spec = yaml.safe_load(f)
        return self._spec
    
    def _build_endpoint_map(self) -> Dict[str, str]:
        """
        Build mapping of endpoint operations to payload files.
        
        Returns:
            Dictionary mapping operation keys (e.g., "GET /planetary/apod 200") to payload file paths
        """
        if self._endpoint_map is not None:
            return self._endpoint_map
        
        spec = self._load_spec()
        endpoint_map = {}
        
        for path, path_item in spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method not in ["get", "post", "put", "delete", "patch"]:
                    continue
                
                operation_id = operation.get("operationId", "")
                responses = operation.get("responses", {})
                
                # Map response codes to payload files
                for status_code, response in responses.items():
                    # Check for x-mock-payload extension
                    mock_payload = response.get("x-mock-payload")
                    if mock_payload:
                        key = f"{method.upper()} {path} {status_code}"
                        endpoint_map[key] = str(self.spec_dir / mock_payload)
                
                # Map request body examples if present
                request_body = operation.get("requestBody", {})
                if request_body:
                    content = request_body.get("content", {})
                    for content_type, content_schema in content.items():
                        mock_request = content_schema.get("x-mock-request")
                        if mock_request:
                            key = f"{method.upper()} {path} request"
                            endpoint_map[key] = str(self.spec_dir / mock_request)
        
        self._endpoint_map = endpoint_map
        return endpoint_map
    
    def get_payload_path(self, method: str, path: str, status_code: str = "200") -> Optional[Path]:
        """
        Get payload file path for an endpoint.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API path (e.g., "/planetary/apod", "/neo/rest/v1/feed")
            status_code: HTTP status code (default: "200")
            
        Returns:
            Path to payload file, or None if not found
        """
        endpoint_map = self._build_endpoint_map()
        key = f"{method.upper()} {path} {status_code}"
        payload_path = endpoint_map.get(key)
        
        if payload_path:
            return Path(payload_path)
        return None
    
    def get_request_payload_path(self, method: str, path: str) -> Optional[Path]:
        """
        Get request payload file path for an endpoint.
        
        Args:
            method: HTTP method (POST, PUT, PATCH)
            path: API path
            
        Returns:
            Path to request payload file, or None if not found
        """
        endpoint_map = self._build_endpoint_map()
        key = f"{method.upper()} {path} request"
        payload_path = endpoint_map.get(key)
        
        if payload_path:
            return Path(payload_path)
        return None
    
    def list_endpoints(self) -> Dict[str, str]:
        """
        List all mapped endpoints.
        
        Returns:
            Dictionary of endpoint keys to payload paths
        """
        return self._build_endpoint_map().copy()

