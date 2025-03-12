import uuid
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.db.database import Base

class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    uti = Column(String, default=lambda: str(uuid.uuid4()), nullable=False)  # Unique Transaction ID
    timestamp = Column(DateTime, default=func.now())
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    request_body = Column(Text, nullable=True)  # Stores request data (nullable)
    response_body = Column(Text, nullable=True)  # Stores response data (nullable)
    message = Column(String, nullable=True)
