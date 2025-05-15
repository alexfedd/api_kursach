from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL, ENVIRONMENT
from sqlalchemy import create_engine
from app.core.models import Base

if ENVIRONMENT == "dev":
    DATABASE_URL = "sqlite+aiosqlite:///./test.db"
    sync_engine = create_engine("sqlite:///./test.db")
else:
    sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", ""))

# Создаем асинхронный движок для работы с базой данных
async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Создаем таблицы
Base.metadata.create_all(bind=sync_engine)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session