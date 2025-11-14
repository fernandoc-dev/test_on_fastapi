"""
Mock for Dronesuite provider for tests
"""
from typing import Dict, Any
import json
from pathlib import Path


class DronesuiteMock:
    """Mock for Dronesuite service"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "payloads" / "dronesuite"
    
    def get_mission_create_success(self) -> Dict[str, Any]:
        """Returns successful mission creation response"""
        payload_path = self.base_path / "mission_create_success.json"
        if payload_path.exists():
            with open(payload_path, "r") as f:
                return json.load(f)
        return {
            "status": "success",
            "mission_id": "12345",
            "message": "Mission created successfully"
        }
    
    def get_mission_create_error(self) -> Dict[str, Any]:
        """Returns error response for mission creation"""
        payload_path = self.base_path / "mission_create_error.json"
        if payload_path.exists():
            with open(payload_path, "r") as f:
                return json.load(f)
        return {
            "status": "error",
            "error_code": "MISSION_CREATE_FAILED",
            "message": "Failed to create mission"
        }

