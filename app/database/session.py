import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.base import Base
from app.database.models import (
    User,
    Specialist,
    Service,
    WorkingSchedule,
    Appointment,
)

from app.database.associations import specialist_services

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite+aiosqlite:///./database.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )
