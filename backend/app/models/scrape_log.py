import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.database import Base
from app.models.opportunity import StringList

class ScrapeLog(Base):
    __tablename__ = "scrape_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String, nullable=False)
    status = Column(String, nullable=False)  # success, failed, partial
    found = Column(Integer, default=0)
    new = Column(Integer, default=0)
    updated = Column(Integer, default=0)
    errors = Column(StringList, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    ran_at = Column(DateTime(timezone=True), default=datetime.utcnow)
