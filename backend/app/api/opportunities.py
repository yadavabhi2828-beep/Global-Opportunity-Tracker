from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityResponse
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=List[OpportunityResponse])
async def list_opportunities(
    category: Optional[str] = None,
    country: Optional[str] = None,
    remote: Optional[bool] = None,
    women_friendly: Optional[bool] = None,
    student_eligible: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve opportunities with optional query filters."""
    stmt = select(Opportunity).where(Opportunity.is_active == True)
    
    if category:
        stmt = stmt.where(Opportunity.category == category)
    if remote is not None:
        stmt = stmt.where(Opportunity.remote == remote)
    if women_friendly is not None:
        stmt = stmt.where(Opportunity.women_friendly == women_friendly)
    if student_eligible is not None:
        stmt = stmt.where(Opportunity.student_eligible == student_eligible)
        
    stmt = stmt.order_by(Opportunity.deadline.asc().nullslast()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    opportunities = result.scalars().all()
    
    # Filter by country in Python if SQLite is used, or handle dynamically
    if country:
        filtered = []
        for opp in opportunities:
            if opp.country and any(c.lower() == country.lower() for c in opp.country):
                filtered.append(opp)
        return filtered
        
    return opportunities

@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(opportunity_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a single opportunity by ID."""
    stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
    result = await db.execute(stmt)
    opp = result.scalars().first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp
