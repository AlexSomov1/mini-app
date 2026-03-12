"""
✅ BACKEND A: ASYNC SQLALCHEMY (ПЕРВАЯ ЗАДАЧА!)
==================================================
Подключение БД + dependency для роутеров

🎯 ЦЕЛЬ: AsyncSession в каждом эндпоинте

⏳ TODO Backend A (завтра!):
1. from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
2. engine = create_async_engine(settings.database_url, echo=True)
3. AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False)

4. @asynccontextmanager
async def get_db(request: Request):
    async with AsyncSessionLocal() as session:
        yield session

5. lifespan app startup → Base.metadata.create_all()

🧪 ТЕСТ:
async def test_db():
    async with get_db() as db:
        result = await db.execute(select(1))
        assert result.scalar() == 1
"""
