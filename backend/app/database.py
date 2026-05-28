from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# Detect if we are using SQLite to handle SQLite-specific connection parameters
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

connect_args = {}
if is_sqlite:
    # Allow multiple threads for SQLite async connection
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=False,
    connect_args=connect_args if is_sqlite else {}
)

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
