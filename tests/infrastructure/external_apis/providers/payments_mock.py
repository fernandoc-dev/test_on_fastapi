"""
Mock for payments provider for tests
"""
from typing import Dict, Any
import json
from pathlib import Path


class PaymentsMock:
    """Mock for payments service"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "payloads" / "payments"
    
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

