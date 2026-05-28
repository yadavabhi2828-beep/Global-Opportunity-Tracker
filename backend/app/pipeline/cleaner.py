from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.models.opportunity import Opportunity
from loguru import logger

async def remove_expired(db: AsyncSession) -> int:
    """Deletes opportunities whose deadlines are before current UTC time."""
    now = datetime.utcnow()
    stmt = delete(Opportunity).where(Opportunity.deadline < now)
    
    try:
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount
    except Exception as e:
        logger.error(f"Failed to remove expired opportunities: {e}")
        await db.rollback()
        return 0
