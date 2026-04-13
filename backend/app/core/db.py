"""
✅ BACKEND A: ASYNC SQLALCHEMY (ПЕРВАЯ ЗАДАЧА!)
==================================================
Подключение БД + dependency для роутеров

🎯 ЦЕЛЬ: AsyncSession в каждом эндпоинте
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.database_url, echo=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
