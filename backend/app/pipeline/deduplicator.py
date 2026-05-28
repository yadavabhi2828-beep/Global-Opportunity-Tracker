from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.opportunity import Opportunity

async def is_duplicate(db: AsyncSession, url_hash: str) -> bool:
    """Check if opportunity hash already exists in DB."""
    stmt = select(Opportunity).where(Opportunity.url_hash == url_hash)
    result = await db.execute(stmt)
    return result.scalars().first() is not None
