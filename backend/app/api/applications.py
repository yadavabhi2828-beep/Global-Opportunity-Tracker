from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.models.application import Application
from app.models.user import User
from app.models.opportunity import Opportunity
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from typing import List
import uuid

router = APIRouter()

VALID_STATUSES = [
    "saved", "planning", "applied", "interview", 
    "accepted", "rejected", "waitlisted"
]

async def ensure_user_exists(db: AsyncSession, user_id: str) -> None:
    """Helper to auto-create user during testing if not present."""
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    if not res.scalars().first():
        user = User(id=user_id, email=f"{user_id}@example.com", name="Test User")
        db.add(user)
        await db.commit()

@router.post("/", response_model=ApplicationResponse)
async def save_opportunity(data: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    """Save an opportunity to a user's tracker."""
    # Ensure foreign keys are met
    await ensure_user_exists(db, data.user_id)
    
    # Check if opportunity exists
    opp_stmt = select(Opportunity).where(Opportunity.id == data.opportunity_id)
    opp_res = await db.execute(opp_stmt)
    opportunity = opp_res.scalars().first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    # Check if duplicate entry already exists
    dup_stmt = select(Application).where(
        Application.user_id == data.user_id,
        Application.opportunity_id == data.opportunity_id
    )
    dup_res = await db.execute(dup_stmt)
    if dup_res.scalars().first():
        raise HTTPException(
            status_code=400, 
            detail="Opportunity already saved in tracker"
        )
        
    app = Application(
        user_id=data.user_id,
        opportunity_id=data.opportunity_id,
        status=data.status,
        priority=data.priority,
        notes=data.notes,
        documents=data.documents or [],
        reminder_date=data.reminder_date,
        applied_at=data.applied_at
    )
    
    db.add(app)
    await db.commit()
    await db.refresh(app)
    
    # Attach opportunity details
    app.opportunity = opportunity
    return app

@router.patch("/{app_id}")
async def update_application(
    app_id: str, 
    data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update details of a tracked application."""
    stmt = select(Application).where(Application.id == app_id)
    res = await db.execute(stmt)
    app = res.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application record not found")
        
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if "status" in updates and updates["status"] not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {VALID_STATUSES}")
        
    for key, val in updates.items():
        setattr(app, key, val)
        
    await db.commit()
    await db.refresh(app)
    return {"message": "Application status updated successfully", "id": app_id}

@router.delete("/{app_id}")
async def delete_application(app_id: str, db: AsyncSession = Depends(get_db)):
    """Remove an application from the tracker."""
    stmt = select(Application).where(Application.id == app_id)
    res = await db.execute(stmt)
    app = res.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application record not found")
        
    await db.delete(app)
    await db.commit()
    return {"message": "Application removed from tracker", "id": app_id}

@router.get("/user/{user_id}", response_model=List[ApplicationResponse])
async def get_my_applications(user_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve all tracked applications for a given user."""
    # Ensure user has a record
    await ensure_user_exists(db, user_id)
    
    stmt = select(Application).where(Application.user_id == user_id)
    result = await db.execute(stmt)
    apps = result.scalars().all()
    
    # Preload corresponding opportunities
    for app in apps:
        opp_stmt = select(Opportunity).where(Opportunity.id == app.opportunity_id)
        opp_res = await db.execute(opp_stmt)
        app.opportunity = opp_res.scalars().first()
        
    return apps
