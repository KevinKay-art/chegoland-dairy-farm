from sqlalchemy import Column, String, Text
from app.database import Base


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(String, nullable=True)