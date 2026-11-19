"""Notification service: console logger by default, pluggable SMS/email."""

from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger("notifications")


class NotificationProvider(ABC):
    @abstractmethod
    def send(self, to: str, message: str, subject: Optional[str] = None) -> bool:
        pass


class ConsoleNotificationProvider(NotificationProvider):
    """Logs notifications to console. Default provider for development."""

    def send(self, to: str, message: str, subject: Optional[str] = None) -> bool:
        logger.info(f"[NOTIFICATION] To: {to} | Subject: {subject or 'N/A'} | Message: {message}")
        print(f"\n--- NOTIFICATION ---\nTo: {to}\nSubject: {subject or 'N/A'}\nMessage: {message}\n------------------\n")
        return True


class NotificationService:
    def __init__(self, provider: Optional[NotificationProvider] = None):
        self.provider = provider or ConsoleNotificationProvider()

    def send_order_confirmation(self, to: str, order_number: str, total_amount: float) -> bool:
        return self.provider.send(
            to,
            f"Your order {order_number} has been received. Total: KES {total_amount:.2f}. We'll notify you when it's out for delivery.",
            subject="Order Confirmation - Chegoland Agri-Empire LTD",
        )

    def send_order_status_update(self, to: str, order_number: str, status: str) -> bool:
        return self.provider.send(
            to,
            f"Your order {order_number} status is now: {status}.",
            subject=f"Order Update - {order_number}",
        )

    def send_sms(self, to: str, message: str) -> bool:
        return self.provider.send(to, message)

    def send_email(self, to: str, subject: str, message: str) -> bool:
        return self.provider.send(to, message, subject=subject)