from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id               = Column(Integer, primary_key=True, index=True)
    service_id       = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at       = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at      = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
