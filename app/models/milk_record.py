from sqlalchemy import Column, String, Float, ForeignKey, Date, Index
from sqlalchemy.orm import relationship
from app.database import Base


class MilkRecord(Base):
    __tablename__ = "milk_records"

    id = Column(String, primary_key=True, index=True)
    cow_id = Column(String, ForeignKey("cows.id"), nullable=False)
    date = Column(Date, nullable=False)
    session = Column(String, nullable=False)  # morning, evening
    yield_litres = Column(Float, nullable=False)
    used_by_calves = Column(Float, default=0.0, nullable=False)
    spoiled = Column(Float, default=0.0, nullable=False)
    available_for_sale = Column(Float, default=0.0, nullable=False)
    notes = Column(String, nullable=True)

    cow = relationship("Cow", back_populates="milk_records")

    __table_args__ = (
        Index("ix_milk_records_cow_id", "cow_id"),
        Index("ix_milk_records_date", "date"),
        Index("ix_milk_records_cow_date", "cow_id", "date"),
    )