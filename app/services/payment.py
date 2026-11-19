"""Payment service: M-Pesa integration and payment processing."""

from typing import Optional, Dict, Any
from app.services.mpesa_service import MpesaService


class PaymentService:
    def __init__(self):
        self.mpesa = MpesaService()

    async def initiate_stk_push(self, phone_number: str, amount: float,
                                account_reference: str, transaction_desc: str) -> Dict[str, Any]:
        return await self.mpesa.stk_push(phone_number, amount, account_reference, transaction_desc)

    async def simulate_callback(self, checkout_request_id: str, success: bool = True,
                                receipt_number: Optional[str] = None,
                                phone_number: Optional[str] = None,
                                amount: Optional[float] = None) -> Dict[str, Any]:
        return await self.mpesa.simulate_callback(
            checkout_request_id, success, receipt_number, phone_number, amount
        )