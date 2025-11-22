"""
Mock for payments API provider for tests.
Loads payloads from tests/infrastructure/external_apis/payments/payloads/
"""
from typing import Dict, Any
import json
from pathlib import Path


class PaymentsMock:
    """Mock for payments API service"""
    
    def __init__(self):
        """Initialize mock with payloads directory"""
        self.base_path = Path(__file__).parent / "payloads"
    
    def get_charge_success(self) -> Dict[str, Any]:
        """Returns successful charge response"""
        payload_path = self.base_path / "charge_success.json"
        if payload_path.exists():
            with open(payload_path, "r") as f:
                return json.load(f)
        return {
            "status": "success",
            "transaction_id": "txn_12345",
            "amount": 100.00,
            "currency": "USD"
        }

