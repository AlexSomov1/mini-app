"""
⏳ BACKEND B: THEMES SERVICE
==================================================
Бизнес-логика тем встреч

📋 ФУНКЦИИ (Backend B):
| Функция | Описание |
|---------|----------|
| create_theme | Создать тему (validate creator !banned) |
| get_themes | Список (?future_only, limit=10) |
| get_theme | Детали темы + кол-во слотов |
| delete_theme | Только creator или admin |

⏳ TODO Неделя 2:
async def create_theme(db, creator: User, theme_ ThemeCreate) -> Theme:
    if creator.is_banned: raise HTTPForbidden
    if theme_data.datetime < datetime.now(): raise HTTPBadRequest
    theme = Theme(**theme_data.dict(), creator_id=creator.id)
    db.add(theme); await db.commit()
    return theme

🧪 ТЕСТЫ:
async def test_create_theme_banned_user():
    creator.is_banned = True
    with pytest.raises(HTTPForbidden): await create_theme(...)
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from datetime import datetime, timezone
from ..models.theme import Theme
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from ..core.db import AsyncSessionLocal
from ..schemas.theme import ThemeCreate
from ..models.user import User

async def create_theme(db: AsyncSession, creator: User, theme_: ThemeCreate) -> Theme:
    if creator.is_banned:
        raise HTTPException(status_code = 403, detail = "Пользователь заблокирован")

    if theme_.datetime < datetime.now(timezone.utc):
        raise HTTPException(status_code = 400, detail = "Некорректная дата встречи")

    theme = Theme(title = theme_.title, description = theme_.description, datetime = theme_.datetime, location = theme_.location,
                 creator_id = creator.id, max_slots = theme_.max_slots)

    db.add(theme)
    await db.commit()

    return theme

async def get_themes(db: AsyncSession) -> list:
    limit = 10

    query = select(Theme)
    query = query.where(Theme.datetime > datetime.now())

    query = query.order_by(Theme.datetime).limit(limit)

    result = await db.execute(query)
    themes = result.scalars().all()

    return themes

async def get_theme(db: AsyncSession, theme_id: int) -> Theme:
    query = select(Theme).where(Theme.id == theme_id)
    result = await db.execute(query)
    exactTheme = result.scalar_one_or_none()

    if exactTheme is None:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    return exactTheme


async def delete_theme(db: AsyncSession, theme_id: int, current_user: User):
    query = select(Theme).where(Theme.id == theme_id)
    result = await db.execute(query)
    exactTheme = result.scalar_one_or_none()

    if exactTheme is None:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    if exactTheme.creator_id != current_user.id: # and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет прав на удаление этой темы")

    await db.delete(exactTheme)
    await db.commit()

    return "Успешное удаление"
