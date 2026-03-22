"""
✅ BACKEND A: МОДЕЛЬ USER (ПЕРВАЯ ЗАДАЧА!)
==================================================
Модель пользователя Telegram (авторизация через initData)

🎯 ЦЕЛЬ: Хранить профиль из Telegram.WebApp.initDataUnsafe
📱 Данные: tg_id (уникальный!) + username + full_name

📋 ПОЛЯ МОДЕЛИ (MVP - обязательно):
| Поле | Тип | Описание | Backend |
|------|-----|----------|---------|
| id | Integer PK | Автоинкремент | Все |
| tg_id | Integer unique | Telegram ID (уник!) | Backend A |
| username | String(32) | @username опционально | Backend A |  
| full_name | String(255) | Имя Фамилия | Backend A |
| is_banned | Boolean | Бан куратором | Backend D |
| created_at | DateTime | Регистрация | Backend A |

⏳ TODO Неделя 2 (Backend A):
1. SQLAlchemy модель с таблицей "users"
2. Pydantic схемы: UserCreate, UserPublic 
3. __repr__() для debug: User(tg_id=123)
4. relationship: themes=[], requests=[]

🧪 ТЕСТИРОВАНИЕ (Backend A):
1. python -c "from app.models.user import User; print('✅ OK')"
2. Base.metadata.create_all() → таблица users
3. INSERT user → UNIQUE tg_id constraint!

🚀 ИСПОЛЬЗОВАНИЕ В API:
@router.get("/me")
async def get_me(init_ str, db: AsyncSession = Depends(get_db)):
    user = await users_service.get_or_create_user(db, init_data)
    return UserPublic.from_orm(user)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, index=True, nullable=True)
    username = Column(String(32), unique=True, index=True)
    full_name = Column(String(255))
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

