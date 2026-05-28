import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, DateTime, TypeDecorator, TEXT
from app.database import Base

class SafeJSON(TypeDecorator):
    """
    Handles JSON columns dynamically:
    - Uses TEXT (storing JSON string) on SQLite/others.
    """
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return "{}"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        try:
            return json.loads(value)
        except Exception:
            return {}

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    profile = Column(SafeJSON, default=dict)  # Stores interests, country, etc.
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
