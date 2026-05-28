import asyncio
import time
from datetime import datetime
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.scrapers import ALL_SCRAPERS
from app.ai.extractor import extract_opportunity
from app.ai.embeddings import generate_embedding, build_embedding_text
from app.pipeline.deduplicator import is_duplicate
from app.pipeline.cleaner import remove_expired
from app.database import AsyncSessionLocal
from app.models.opportunity import Opportunity
from app.models.scrape_log import ScrapeLog

async def run_daily_pipeline():
    """Runs the entire discovery, extraction, deduplication, and indexing pipeline."""
    logger.info("Starting opportunity discovery pipeline run...")
    start_time = time.time()
    
    total_new = 0
    total_found = 0
    
    async with AsyncSessionLocal() as db:
        # Step 1: Clean expired items
        removed_count = await remove_expired(db)
        logger.info(f"Cleaned {removed_count} expired opportunities from database.")
        
        # Step 2: Iterate over all configured scrapers
        for scraper in ALL_SCRAPERS:
            scraper_start = time.time()
            errors = []
            found_count = 0
            new_count = 0
            
            logger.info(f"Running scraper: {scraper.source_name} ...")
            try:
                raw_items = await scraper.discover()
                found_count = len(raw_items)
                total_found += found_count
                
                for item in raw_items:
                    # Deduplication check
                    if await is_duplicate(db, item["url_hash"]):
                        continue
                    
                    # AI Extraction
                    extracted = await extract_opportunity(item["raw_content"], item["url"])
                    if not extracted or not extracted.name:
                        continue
                    
                    # Embeddings text build & generation
                    extracted_dict = extracted.model_dump()
                    embed_text = build_embedding_text(extracted_dict)
                    embedding = await generate_embedding(embed_text)
                    
                    # Parsing date string safely
                    deadline_dt = None
                    if extracted.deadline:
                        try:
                            deadline_dt = datetime.strptime(extracted.deadline, "%Y-%m-%d")
                        except Exception:
                            pass
                            
                    # Construct database model
                    opp = Opportunity(
                        name=extracted.name,
                        organization=extracted.organization,
                        description=extracted.description,
                        url=item["url"],
                        url_hash=item["url_hash"],
                        category=extracted.category,
                        tags=extracted.tags,
                        country=extracted.country,
                        remote=extracted.remote,
                        eligibility_text=extracted.eligibility,
                        women_friendly=extracted.women_friendly,
                        indian_eligible=extracted.indian_eligible,
                        student_eligible=extracted.student_eligible,
                        min_age=extracted.min_age,
                        max_age=extracted.max_age,
                        application_fee=extracted.application_fee,
                        funding_amount=extracted.funding_amount,
                        deadline=deadline_dt,
                        source=item["source"],
                        embedding=embedding,
                        is_active=True
                    )
                    
                    db.add(opp)
                    new_count += 1
                    total_new += 1
                    
                    # Prevent API rate-limiting issues
                    await asyncio.sleep(0.5)
                
                await db.commit()
                status = "success"
                
            except Exception as e:
                logger.error(f"Scraper '{scraper.source_name}' encountered an error: {e}")
                errors.append(str(e))
                await db.rollback()
                status = "failed"
            
            # Log run metrics in Database
            duration = int((time.time() - scraper_start) * 1000)
            log_entry = ScrapeLog(
                source=scraper.source_name,
                status=status,
                found=found_count,
                new=new_count,
                errors=errors,
                duration_ms=duration
            )
            db.add(log_entry)
            await db.commit()
            
    total_duration = int((time.time() - start_time) * 1000)
    logger.info(f"Pipeline finished. Found: {total_found}, New Added: {total_new}. Duration: {total_duration}ms")
    return {
        "status": "complete",
        "found": total_found,
        "new": total_new,
        "duration_ms": total_duration
    }
