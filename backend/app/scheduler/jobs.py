from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.pipeline.orchestrator import run_daily_pipeline
from app.notifications import send_deadline_reminder
from app.database import AsyncSessionLocal
from app.models.application import Application
from app.models.opportunity import Opportunity
from app.models.user import User
from sqlalchemy import select
from datetime import datetime, timedelta
from loguru import logger
import pytz

# Setup daily schedule runner
scheduler = AsyncIOScheduler(timezone=pytz.utc)

async def check_upcoming_deadlines():
    """Checks for applications whose deadline is tomorrow and sends email reminders."""
    logger.info("Running automated deadline reminder checker...")
    tomorrow_start = datetime.utcnow().date() + timedelta(days=1)
    tomorrow_end = tomorrow_start + timedelta(days=1)
    
    async with AsyncSessionLocal() as db:
        # Select applications where opportunity deadline is tomorrow
        stmt = select(Application)
        result = await db.execute(stmt)
        apps = result.scalars().all()
        
        sent_count = 0
        for app in apps:
            opp_stmt = select(Opportunity).where(Opportunity.id == app.opportunity_id)
            opp_res = await db.execute(opp_stmt)
            opp = opp_res.scalars().first()
            
            if opp and opp.deadline:
                opp_date = opp.deadline.date()
                if tomorrow_start <= opp_date < tomorrow_end:
                    user_stmt = select(User).where(User.id == app.user_id)
                    user_res = await db.execute(user_stmt)
                    user = user_res.scalars().first()
                    
                    if user and user.email:
                        await send_deadline_reminder(
                            user_email=user.email,
                            opportunity_name=opp.name,
                            deadline=opp.deadline.strftime("%Y-%m-%d")
                        )
                        sent_count += 1
        logger.info(f"Deadline checks finished. Sent {sent_count} reminders.")

def start_scheduler():
    try:
        # Scraper runner daily
        scheduler.add_job(
            run_daily_pipeline,
            trigger="cron",
            hour=2,
            minute=0,
            id="daily_pipeline_job",
            replace_existing=True
        )
        # Reminders runner daily at 8:00 AM UTC
        scheduler.add_job(
            check_upcoming_deadlines,
            trigger="cron",
            hour=8,
            minute=0,
            id="daily_deadline_check_job",
            replace_existing=True
        )
        scheduler.start()
        logger.info("Daily opportunity discovery scheduler active (Runs at 2:00 AM UTC).")
        logger.info("Daily deadline reminder scheduler active (Runs at 8:00 AM UTC).")
    except Exception as e:
        logger.error(f"Failed to start schedule manager: {e}")

