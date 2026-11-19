from sqlalchemy import Column, String, ForeignKey, Date, Text, Index
from sqlalchemy.orm import relationship
from app.database import Base


class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(String, primary_key=True, index=True)
    cow_id = Column(String, ForeignKey("cows.id"), nullable=False)
    record_type = Column(String, nullable=False)  # health, vaccination
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=False)
    next_due_date = Column(Date, nullable=True)
    cost = Column(String, nullable=True)
    vet_name = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    cow = relationship("Cow", back_populates="health_records")

    __table_args__ = (
        Index("ix_health_records_cow_id", "cow_id"),
        Index("ix_health_records_date", "date"),
    )