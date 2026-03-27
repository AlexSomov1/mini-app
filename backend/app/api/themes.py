"""
⏳ BACKEND B: API THEMES ROUTER (CRUD)
==================================================
/api/v1/themes/* — создание/список тем встреч

🎯 ЦЕЛЬ: Студент создаёт тему → другие подают заявки

📋 ЭНДПОИНТЫ (Backend B, Неделя 2):
| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | /themes | Список тем (?limit=10) | public |
| POST | /themes | Создать тему | user |
| GET | /themes/{id} | Детали темы | public |
| DELETE | /themes/{id} | Удалить (creator/admin) | creator |

⏳ TODO Backend B:
1. APIRouter(prefix="/api/v1/themes", tags=["themes"])
2. GET /themes?limit=10&offset=0&future_only=true
3. POST /themes (ThemeCreate + current_user)
4. validate: !user.is_banned, datetime > now()

🧪 ТЕСТИРОВАНИЕ:
GET /api/v1/themes → [{"id":1,"title":"Матан","datetime":"2026-03-15T19:00"}]

POST /api/v1/themes
{
  "title": "Матан с Петровым",
  "datetime": "2026-03-15T19:00",
  "location": "ауд.305"
}
→ 201 {"id":1,...}

🔐 ПРАВА ДОСТУПА:
- GET: все студенты
- POST: только !is_banned
- DELETE: creator_id == current_user.id ИЛИ admin
"""

from fastapi import APIRouter
from sqlalchemy import select
from ..models.theme import Theme
from ..models.user import User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from ..core.db import AsyncSessionLocal
from ..schemas.theme import ThemeCreate
from ..services.themes_service import create_theme, get_theme, get_themes, delete_theme
from app.api.users import get_me

router = APIRouter(prefix="/api/v1/themes", tags=["themes"])

#получение текущего пользователя (пока что заглушка)
async def get_current_user(db: AsyncSession) -> User:
    result = await db.execute(
        select(User).where(User.tg_id == 12377331)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            tg_id=12377331,
            username="test",
            full_name="test",
            is_banned=False,
            is_admin=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user

@router.get("/", summary="Получить список всех тем")
async def get_all_themes():
  async with AsyncSessionLocal() as session:
    result = await get_themes(session)

    return result

@router.get("/{id}", summary = "Получить детали темы по id")
async def get_theme_data(theme_id: int):
  async with AsyncSessionLocal() as session:
    result = await get_theme(session, theme_id)

  return result

@router.post("/themes", summary = "Опубликовать тему")
async def create_theme(themeToCreate: ThemeCreate):
  async with AsyncSessionLocal() as session:
    user = await get_me(session)
    result = await create_theme(session, user, themeToCreate)

  return result

@router.delete("/themes/{id}", summary = "Удалить тему")
async def delete_theme(theme_id: int):
  async with AsyncSessionLocal() as session:
    user = await get_me(session)
    await delete_theme(session, theme_id, user)

  return "deleted"
