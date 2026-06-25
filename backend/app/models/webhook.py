from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Webhook(Base):
    __tablename__ = "webhooks"

    id         = Column(Integer, primary_key=True, index=True)
    url        = Column(String(500), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=True, index=True)
    on_down    = Column(Boolean, default=True, nullable=False)
    on_recover = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
