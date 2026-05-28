from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.database import engine, Base
from app.api import opportunities, applications, search, admin
from app.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Database schema creation
    logger.info("Initializing database models...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully.")
    
    # Startup: Scheduler start
    start_scheduler()
    yield
    # Shutdown logic if any goes here
    logger.info("Shutting down API server...")

app = FastAPI(
    title="Global Opportunity Tracker API",
    version="1.0.0",
    description="AI-powered pipeline to discover, extract, and track global opportunities.",
    lifespan=lifespan
)

# Enable CORS for Next.js app running locally on port 3000 or 3001
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect endpoints
app.include_router(opportunities.router, prefix="/api/opportunities", tags=["Opportunities"])
app.include_router(applications.router, prefix="/api/applications", tags=["Tracker"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "opportunity-tracker-api"}
