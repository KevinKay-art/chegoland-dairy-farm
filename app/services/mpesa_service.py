"""M-Pesa Daraja STK Push service with mock mode for development/demo."""

import base64
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import httpx
from app.config import settings


class MpesaService:
    """Wrapper around Safaricom M-Pesa Daraja API. Falls back to mock mode when keys are absent."""

    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.business_short_code = settings.MPESA_BUSINESS_SHORT_CODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL
        self.mock_mode = settings.MPESA_MOCK_MODE or not (self.consumer_key and self.consumer_secret and self.passkey)
        self.base_url = "https://sandbox.safaricom.co.ke" if settings.MPESA_ENVIRONMENT == "sandbox" else "https://api.safaricom.co.ke"

    def _get_access_token(self) -> Optional[str]:
        if self.mock_mode:
            return "mock_access_token"
        try:
            auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
            headers = {"Authorization": f"Basic {auth}"}
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials", headers=headers)
                resp.raise_for_status()
                return resp.json().get("access_token")
        except Exception:
            return None

    def _generate_password(self, timestamp: str) -> str:
        data = f"{self.business_short_code}{self.passkey}{timestamp}"
        return base64.b64encode(data.encode()).decode()

    async def stk_push(self, phone_number: str, amount: float, account_reference: str, transaction_desc: str) -> Dict[str, Any]:
        """Initiate STK Push. Returns dict with success, checkout_request_id, message, etc."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

        if self.mock_mode:
            checkout_request_id = f"mock_ws_CO{uuid.uuid4().hex[:14]}"
            return {
                "success": True,
                "checkout_request_id": checkout_request_id,
                "merchant_request_id": f"mock_merchant_{uuid.uuid4().hex[:10]}",
                "response_code": "0",
                "response_description": "Success. Request accepted for processing (MOCK)",
                "customer_message": "Success. Request accepted for processing (MOCK)",
                "mock_mode": True,
            }

        token = self._get_access_token()
        if not token:
            return {
                "success": False,
                "error": "Failed to obtain M-Pesa access token",
                "mock_mode": False,
            }

        password = self._generate_password(timestamp)
        payload = {
            "BusinessShortCode": self.business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.business_short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url or f"{self.base_url}/mpesa/callback",
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }

        try:
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(f"{self.base_url}/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return {
                    "success": data.get("ResponseCode") == "0",
                    "checkout_request_id": data.get("CheckoutRequestID"),
                    "merchant_request_id": data.get("MerchantRequestID"),
                    "response_code": data.get("ResponseCode"),
                    "response_description": data.get("ResponseDescription"),
                    "customer_message": data.get("CustomerMessage"),
                    "mock_mode": False,
                }
        except Exception as e:
            return {"success": False, "error": str(e), "mock_mode": False}

    async def simulate_callback(self, checkout_request_id: str, success: bool = True,
                                receipt_number: Optional[str] = None,
                                phone_number: Optional[str] = None,
                                amount: Optional[float] = None) -> Dict[str, Any]:
        """Simulate an M-Pesa callback (mock mode only). Useful for testing/demo."""
        if not self.mock_mode:
            return {"error": "Simulation only available in mock mode"}
        result_code = "0" if success else "1"
        result_desc = "The service request is processed successfully." if success else "The service request failed."
        return {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": checkout_request_id,
                    "MerchantRequestID": f"mock_merchant_{uuid.uuid4().hex[:10]}",
                    "ResultCode": result_code,
                    "ResultDesc": result_desc,
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": amount or 0.0},
                            {"Name": "MpesaReceiptNumber", "Value": receipt_number or f"MOCK{uuid.uuid4().hex[:10].upper()}"},
                            {"Name": "PhoneNumber", "Value": phone_number or "254700000000"},
                        ]
                    },
                }
            }
        }