import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ARRAY, JSON, text, TypeDecorator, TEXT
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from app.database import Base

class SafeVector(TypeDecorator):
    """
    Handles vector embeddings dynamically:
    - Uses pgvector Vector type on PostgreSQL.
    - Falls back to TEXT (storing JSON strings) on SQLite.
    """
    impl = TEXT
    cache_ok = True

    def __init__(self, dimensions=1536):
        super().__init__()
        self.dimensions = dimensions

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector(self.dimensions))
        return dialect.type_descriptor(TEXT())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            # pgvector handles list of floats directly
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            # pgvector returns list of floats (or numpy array depending on config)
            return list(value)
        return json.loads(value)

class StringList(TypeDecorator):
    """
    Handles lists of strings:
    - Uses ARRAY(String) on PostgreSQL.
    - Falls back to TEXT (storing JSON arrays) on SQLite.
    """
    impl = TEXT
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String))
        return dialect.type_descriptor(TEXT())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        if dialect.name == "postgresql":
            return list(value)
        try:
            return json.loads(value)
        except Exception:
            return []

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    description = Column(String, nullable=True)
    url = Column(String, nullable=False)
    url_hash = Column(String, unique=True, nullable=False)
    
    category = Column(String, nullable=True)  # scholarship, fellowship, accelerator, grant, etc.
    tags = Column(StringList, nullable=True)     # ['AI', 'Startup', 'Women']
    type = Column(String, nullable=True)     # funding, competition, conference, etc.
    
    country = Column(StringList, nullable=True)  # ['India', 'USA']
    region = Column(String, nullable=True)     # Asia, Europe, Global
    remote = Column(Boolean, default=False)
    in_person = Column(Boolean, default=False)
    
    eligibility_text = Column(String, nullable=True)
    women_friendly = Column(Boolean, default=False)
    indian_eligible = Column(Boolean, default=False)
    student_eligible = Column(Boolean, default=False)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    application_fee = Column(String, nullable=True)
    
    funding_amount = Column(String, nullable=True)
    funding_currency = Column(String, nullable=True)
    
    deadline = Column(DateTime(timezone=True), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    ai_summary = Column(String, nullable=True)
    embedding = Column(SafeVector(1536), nullable=True)
    
    source = Column(String, nullable=True)
    last_checked = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
