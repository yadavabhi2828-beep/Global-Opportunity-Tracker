from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.scrape_log import ScrapeLog
from app.pipeline.orchestrator import run_daily_pipeline
from typing import List

router = APIRouter()

@router.post("/trigger-pipeline")
async def trigger_pipeline(background_tasks: BackgroundTasks):
    """Triggers the web scraper engine manually as a background task."""
    background_tasks.add_task(run_daily_pipeline)
    return {"message": "Opportunity discovery pipeline triggered in background"}

@router.get("/scrape-logs")
async def list_scrape_logs(limit: int = 15, db: AsyncSession = Depends(get_db)):
    """Retrieve history of scraper actions and performance statistics."""
    stmt = select(ScrapeLog).order_by(ScrapeLog.ran_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
