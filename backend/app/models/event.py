from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id           = Column(Integer, primary_key=True, index=True)
    service_id   = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"))
    is_up        = Column(Boolean, nullable=False)
    response_ms  = Column(Float, nullable=True)
    status_code  = Column(Integer, nullable=True)
    error_detail = Column(String(500), nullable=True)
    checked_at   = Column(DateTime(timezone=True), server_default=func.now())