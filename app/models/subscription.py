from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    frequency = Column(String, default="daily", nullable=False)  # daily, weekly
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    next_delivery_date = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    user = relationship("User", back_populates="subscriptions")

    __table_args__ = (
        Index("ix_subscriptions_user_id", "user_id"),
        Index("ix_subscriptions_product_id", "product_id"),
        Index("ix_subscriptions_is_active", "is_active"),
    )