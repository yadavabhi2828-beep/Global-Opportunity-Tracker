from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OpportunityBase(BaseModel):
    name: str
    organization: Optional[str] = None
    description: Optional[str] = None
    url: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    type: Optional[str] = None
    country: Optional[List[str]] = None
    region: Optional[str] = None
    remote: bool = False
    in_person: bool = False
    eligibility_text: Optional[str] = None
    women_friendly: bool = False
    indian_eligible: bool = False
    student_eligible: bool = False
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    application_fee: Optional[str] = None
    funding_amount: Optional[str] = None
    funding_currency: Optional[str] = None
    deadline: Optional[datetime] = None
    start_date: Optional[datetime] = None
    is_active: bool = True
    is_verified: bool = False
    ai_summary: Optional[str] = None

class OpportunityCreate(OpportunityBase):
    url_hash: str
    source: Optional[str] = None
    embedding: Optional[List[float]] = None

class OpportunityUpdate(BaseModel):
    name: Optional[str] = None
    organization: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    country: Optional[List[str]] = None
    remote: Optional[bool] = None
    eligibility_text: Optional[str] = None
    deadline: Optional[datetime] = None
    funding_amount: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class OpportunityResponse(OpportunityBase):
    id: str
    source: Optional[str] = None
    last_checked: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
