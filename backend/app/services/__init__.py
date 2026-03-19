"""
💼 БИЗНЕС-ЛОГИКА SERVICES (чистые функции)
==================================================
Разделение ответственности: Models → Services → API

🎯 ЦЕЛЬ: Логика без привязки к БД/framework
📱 Вызов: api → service → model

✅ Backend A: users_service.py (get_or_create_user)
⏳ Backend B: themes_service.py (CRUD + validate)
⏳ Backend C: requests_service.py (moderate + notify)

🔧 ПРИМЕР ИСПОЛЬЗОВАНИЯ:
from app.services.users_service import get_or_create_user

@router.get("/me")
async def get_me(db: AsyncSession):
    user = await get_or_create_user(db, init_data)
    return UserPublic.model_validate(user)

🚀 ПРАВИЛА SERVICES:
- Только async def
- Только параметры: db: AsyncSession + data
- Нет HTTP/Telegram зависимостей
- 100% unit тесты в tests/unit/test_users.py
"""
