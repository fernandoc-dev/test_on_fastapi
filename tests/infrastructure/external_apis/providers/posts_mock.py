"""
Mock for Posts API provider for tests.
Loads assets from tests/infrastructure/external_apis/assets/posts/
"""
from typing import Dict, Any, List, Optional
import json
from pathlib import Path


class PostsMock:
    """Mock for Posts API service"""
    
    def __init__(self):
        """Initialize mock with assets directory"""
        self.base_path = Path(__file__).parent.parent / "assets" / "posts"
    
    def _load_json_file(self, filename: str) -> Any:
        """
        Load JSON file from assets directory.
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            Parsed JSON content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        file_path = self.base_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Asset file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_all_posts(self) -> List[Dict[str, Any]]:
        """Returns list of all posts from assets"""
        return self._load_json_file("get_posts_all.json")
    
    def get_post_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        """
        Returns post by ID from assets.
        
        Args:
            post_id: Post ID to retrieve
            
        Returns:
            Post data if found, None otherwise
        """
        try:
            return self._load_json_file(f"get_post_by_id_{post_id}.json")
        except FileNotFoundError:
            return None
    
    def get_create_request(self) -> Dict[str, Any]:
        """Returns example post creation request from assets"""
        return self._load_json_file("post_create_request.json")
    
    def get_create_response(self) -> Dict[str, Any]:
        """Returns example post creation response from assets"""
        return self._load_json_file("post_create_response.json")
    
    def get_update_request(self) -> Dict[str, Any]:
        """Returns example post update request from assets"""
        return self._load_json_file("post_update_request.json")
    
    def get_update_response(self) -> Dict[str, Any]:
        """Returns example post update response from assets"""
        return self._load_json_file("post_update_response.json")
    
    def get_not_found_error(self) -> Dict[str, Any]:
        """Returns 404 error response from assets"""
        return self._load_json_file("post_not_found_404.json")

