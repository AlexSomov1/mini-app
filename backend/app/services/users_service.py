"""
✅ BACKEND A: USERS SERVICE (бизнес-логика)
==================================================
Чистые функции для работы с пользователями

🎯 ЦЕЛЬ: get_or_create_user из Telegram initData

📋 ФУНКЦИИ (Backend A, Неделя 2):
| Функция | Параметры | Возврат | Описание |
|---------|-----------|---------|----------|
| get_or_create_user | db, init_dict | User | Создать/найти по tg_id |
| get_user_by_tg_id | db, tg_id:int | User | Только чтение |
| ban_user | db, user_id:int, ban:bool | bool | Бан/разбан |

⏳ TODO Backend A:
1. async def get_or_create_user(db: AsyncSession, init_ dict) -> User:
2. user = await db.get(User, init_data["user"]["id"])
3. if not user: user = User(**init_data["user"]); db.add(user)
4. await db.commit(); await db.refresh(user); return user

🧪 UNIT ТЕСТЫ (tests/unit/test_users.py):
@pytest.mark.asyncio
async def test_get_or_create_user():
    init_data = {"user": {"id":123, "username":"@test"}}
    user = await get_or_create_user(db, init_data)
    assert user.tg_id == 123
    assert user.username == "@test"

🔐 VALIDATION initData:
- Проверить hash(init_data) == init_data["hash"]
- Только trusted Telegram данные
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

async def get_or_create_user(db: AsyncSession, tg_id: int, username: str | None, full_name: str) -> User:
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(tg_id=tg_id, username=username, full_name=full_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

async def get_user_by_tg_id(db: AsyncSession, tg_id: int) -> User | None:
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    return result.scalar_one_or_none()

async def ban_user(db: AsyncSession, user_id: int, ban: bool) -> bool:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return False

    user.is_banned = ban
    await db.commit()
    return True