from sqlalchemy import Column, String, Float, Date, Text, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Cow(Base):
    __tablename__ = "cows"

    id = Column(String, primary_key=True, index=True)
    tag_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    breed = Column(String, nullable=False)  # Friesian, Ayrshire, Jersey, Guernsey
    date_of_birth = Column(Date, nullable=True)
    photo_url = Column(String, nullable=True)
    status = Column(String, default="lactating", nullable=False)  # lactating, dry, pregnant, sick
    daily_avg_yield = Column(Float, default=0.0, nullable=False)
    notes = Column(Text, nullable=True)

    milk_records = relationship("MilkRecord", back_populates="cow", cascade="all, delete-orphan")
    health_records = relationship("HealthRecord", back_populates="cow", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_cows_breed", "breed"),
        Index("ix_cows_status", "status"),
    )