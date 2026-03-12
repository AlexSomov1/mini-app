"""
🗃️ SQLALCHEMY ORM МОДЕЛИ БАЗЫ ДАННЫХ
==================================================
Backend A,B,C: создавайте модели здесь!

🎯 ЦЕЛЬ: SQLAlchemy async модели для SQLite/PostgreSQL
📊 База: app.db (SQLite для разработки)

✅ ГОТОВО (Backend A):
from .user import User, UserCreate, UserPublic

⏳ TODO Неделя 2:
from .theme import Theme, ThemeCreate, ThemePublic  # Backend B
from .request import Request, RequestCreate  # Backend C

🔧 ИСПОЛЬЗОВАНИЕ:
from app.core.db import get_db
async with get_db() as session:
    user = await session.get(User, tg_id=123456)
    themes = await session.execute(select(Theme).limit(10))

🧪 ТЕСТЫ (Backend A создаст conftest.py):
@pytest.mark.asyncio
async def test_user_create():
    async with get_db() as session:
        user = User(tg_id=123)
        session.add(user)
        await session.commit()
        assert user.id > 0

📋 СВЯЗИ МЕЖДУ МОДЕЛЯМИ (Неделя 2):
User.themes = relationship("Theme", back_populates="creator")
Theme.creator = relationship("User", back_populates="themes")
Theme.requests = relationship("Request", back_populates="theme")
Request.theme = relationship("Theme", back_populates="requests")
Request.user = relationship("User", back_populates="requests")

🚀 АВТОСОЗДАНИЕ ТАБЛИЦ (app/core/db.py):
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
"""