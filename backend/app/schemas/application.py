from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.opportunity import OpportunityResponse

class ApplicationBase(BaseModel):
    status: str = "saved"
    priority: int = 3
    notes: Optional[str] = None
    documents: Optional[List[Dict[str, Any]]] = None
    reminder_date: Optional[datetime] = None
    applied_at: Optional[datetime] = None

class ApplicationCreate(ApplicationBase):
    user_id: str
    opportunity_id: str

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[int] = None
    notes: Optional[str] = None
    documents: Optional[List[Dict[str, Any]]] = None
    reminder_date: Optional[datetime] = None
    applied_at: Optional[datetime] = None

class ApplicationResponse(ApplicationBase):
    id: str
    user_id: str
    opportunity_id: str
    created_at: datetime
    updated_at: datetime
    opportunity: Optional[OpportunityResponse] = None

    class Config:
        from_attributes = True
