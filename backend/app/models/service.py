from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Service(Base):
    __tablename__ = "services"

    id                   = Column(Integer, primary_key=True, index=True)
    name                 = Column(String(100), nullable=False)
    url                  = Column(String(500), nullable=False)
    is_active            = Column(Boolean, default=True)
    check_interval       = Column(Integer, default=60, nullable=False)
    expected_status_code = Column(Integer, default=200, nullable=False)
    timeout_seconds      = Column(Integer, default=10, nullable=False)
    tags                 = Column(String(200), nullable=True)
    created_at           = Column(DateTime(timezone=True), server_default=func.now())
    updated_at           = Column(DateTime(timezone=True), onupdate=func.now())