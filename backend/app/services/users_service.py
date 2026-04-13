"""
✅ BACKEND A: USERS SERVICE (ПОЛНОЕ ОПИСАНИЕ)
==================================================
Бизнес-логика пользователей: создание из Telegram initData, поиск,
бан/разбан, получение по различным идентификаторам и проверки статуса.

🎯 ЦЕЛЬ ФАЙЛА:
Users service — единственная точка работы с пользователями в бизнес-логике.
Здесь ВСЕ правила:
- валидация Telegram initData (hash проверка);
- создание/поиск пользователя по tg_id;
- бан/разбан пользователей;
- получение пользователя по id/tg_id/username;
- проверка статуса (banned, admin);
- статистика пользователей.

API-слой (app/api/users.py) только вызывает service функции.

--------------------------------------------------
📦 ЗОНА ОТВЕТСТВЕННОСТИ USERS SERVICE
--------------------------------------------------
Users service отвечает за:

1. Создание/поиск пользователя из Telegram initData с проверкой hash.
2. Получение пользователя по tg_id, database id или username.
3. Бан/разбан пользователей (с логикой полей).
4. Проверку прав (is_admin, is_banned).
5. Подсчет статистики пользователей.
6. Бизнес-валидацию:
   - подлинность Telegram initData;
   - уникальность tg_id/username;
   - права администратора;
   - статус пользователя.

--------------------------------------------------
📋 ОСНОВНЫЕ ФУНКЦИИ ФАЙЛА
--------------------------------------------------
| Функция | Назначение | Кто вызывает |
|---------|------------|--------------|
| get_or_create_user | Создать/найти из Telegram initData | Telegram webhook, auth middleware |
| get_user_by_tg_id | Найти по Telegram ID | Все сервисы (themes, requests) |
| get_user_by_id | Найти по database ID | API endpoints |
| ban_user | Забанить/разбанить | Admin API |
| is_user_banned | Проверка статуса бана | Themes/Requests service |
| is_user_admin | Проверка прав админа | Authorization |
| get_user_stats | Статистика пользователей | Admin dashboard |

--------------------------------------------------
🧱 ПРЕДПОЛАГАЕМЫЕ ЗАВИСИМОСТИ
--------------------------------------------------
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, Dict, Tuple, List
from hashlib import sha256
from hmac import HMAC
import time
from datetime import datetime

from app.models.user import User
from app.core.config import settings  # TELEGRAM_BOT_TOKEN
from app.core.security import verify_telegram_init_data  # hash проверка

--------------------------------------------------
🧠 БИЗНЕС-ПРАВИЛА ПОЛЬЗОВАТЕЛЕЙ
--------------------------------------------------
1. Telegram initData должен пройти hash валидацию.
2. tg_id уникален — один Telegram аккаунт = один User.
3. username может меняться — хранить first_name/last_name.
4. Бан: is_banned=True блокирует создание тем/заявок.
5. Админ: список admin_tg_ids в settings.
6. Поиск по username — case-insensitive, с LIKE '%username%'.
7. Soft limits: не более 1 запроса в секунду на создание user.

--------------------------------------------------
🧩 ПОЛНАЯ СИГНАТУРА ФУНКЦИЙ
--------------------------------------------------

1. GET_OR_CREATE FROM TELEGRAM
async def get_or_create_user(
    db: AsyncSession,
    init_ dict
) -> User:

2. GET BY TELEGRAM ID
async def get_user_by_tg_id(
    db: AsyncSession,
    tg_id: int
) -> Optional[User]:

3. GET BY DATABASE ID
async def get_user_by_id(
    db: AsyncSession,
    user_id: int
) -> Optional[User]:

4. BAN/UNBAN
async def ban_user(
    db: AsyncSession,
    user_id: int,
    is_banned: bool,
    admin_id: int  # кто банит
) -> User:

5. STATUS CHECKS
def is_user_banned(user: User) -> bool:
def is_user_admin(user: User, admin_tg_ids: list) -> bool:

--------------------------------------------------
✅ ПОЛНОЕ ПОВЕДЕНИЕ get_or_create_user()
--------------------------------------------------
Функция обязана выполнить 7 шагов:

1. Валидация initData:
   verify_telegram_init_data(init_data, settings.TELEGRAM_BOT_TOKEN)

2. Извлечь данные:
   user_data = init_data["user"]
   tg_id = user_data["id"]
   username = user_data.get("username")
   first_name = user_data.get("first_name")

3. Найти существующего:
   user = await db.get(User, tg_id, options=[selectinload(User.requests)])

4. Если НЕ существует:
   user = User(
       tg_id=tg_id,
       username=username,
       first_name=first_name,
       last_name=user_data.get("last_name"),
       is_banned=False,
       is_admin=False  # только ручная установка
   )
   db.add(user)
   await db.commit()
   await db.refresh(user)

5. Обновить данные (если username/first_name изменились):
   if user.username != username or user.first_name != first_name:
       user.username = username
       user.first_name = first_name
       await db.commit()
       await db.refresh(user)

6. Вернуть ORM объект User с подгруженными relations.

Ошибки:
- BadRequestError("Invalid Telegram initData")
- ConflictError("User already exists with different tg_id")

--------------------------------------------------
✅ TELEGRAM INITDATA ВАЛИДАЦИЯ
--------------------------------------------------
def verify_telegram_init_data( dict, bot_token: str) -> None:
    Проверяет подлинность Telegram initData по алгоритму https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    received_hash = data["hash"]
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()) if k != "hash")
    secret_key = hmac.new(
        ("WebAppData".encode() + bot_token.encode()),
        msg=hashlib.sha256,
        digestmod=hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(
        secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(calculated_hash, received_hash):
        raise ValueError("Invalid Telegram initData hash")

--------------------------------------------------
✅ ПОЛНОЕ ПОВЕДЕНИЕ ban_user()
--------------------------------------------------
Функция обязана:

1. Найти пользователя: await get_user_by_id(db, user_id)
2. Проверить админа: await is_user_admin(admin_user, settings.ADMIN_TG_IDS)
3. Обновить статус:
   user.is_banned = is_banned
   user.banned_at = datetime.utcnow() if is_banned else None
   await db.commit()
4. Логировать действие (опционально):
   # audit log или уведомление админам
5. Вернуть обновленного пользователя.

Ошибки:
- NotFoundError("User not found")
- ForbiddenError("Admin rights required")
- BadRequestError("Cannot ban admin user") (если есть защита)

--------------------------------------------------
✅ ПОЛНОЕ ПОВЕДЕНИЕ get_user_by_tg_id()
--------------------------------------------------
async def get_user_by_tg_id(db: AsyncSession, tg_id: int) -> Optional[User]:
    if tg_id <= 0:
        raise ValueError("Invalid Telegram ID")
    
    stmt = select(User).where(User.tg_id == tg_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

Особенности:
- Быстрый поиск по индексированному полю tg_id.
- Возвращает None при отсутствии (не выбрасывает ошибку).
- Используется из themes/requests сервисов.

--------------------------------------------------
✅ STATUS CHECK FUNCTIONS
--------------------------------------------------
def is_user_banned(user: User) -> bool:
    Пользователь забанен.
    return bool(user.is_banned)

def is_user_admin(user: User, admin_tg_ids: List[int]) -> bool:
    Пользователь администратор.
    return user.tg_id in admin_tg_ids

def can_create_themes(user: User) -> bool:
    Может ли пользователь создавать темы.
    return not user.is_banned

def can_submit_requests(user: User) -> bool:
    Может ли пользователь подавать заявки.
    return not user.is_banned

--------------------------------------------------
✅ SUPPORT ФУНКЦИИ
--------------------------------------------------

1. Поиск по username (case-insensitive):
async def search_users(
    db: AsyncSession,
    username: str,
    limit: int = 10
) -> List[User]:

2. Статистика:
async def get_user_stats(db: AsyncSession) -> Dict:
Возвращает:
{
    "total_users": 1250,
    "banned_users": 15,
    "active_users": 1235,
    "admins": 3,
    "created_last_7d": 42
}

3. Список админов:
async def get_admin_users(db: AsyncSession) -> List[User]:

--------------------------------------------------
🔄 ТРАНЗАКЦИИ
--------------------------------------------------
get_or_create_user и ban_user работают с транзакциями:

async def get_or_create_user(...):
    try:
        # валидация + создание/обновление
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise ConflictError("User already exists")
    except Exception:
        await db.rollback()
        raise

async def ban_user(...):
    try:
        # проверки + update
        await db.commit()
        return user
    except Exception:
        await db.rollback()
        raise

--------------------------------------------------
🧪 ПОЛНЫЙ СПИСОК ТЕСТОВ (test_users_service.py)
--------------------------------------------------
get_or_create_user (8 тестов):
1. ✓ Новый пользователь создается
2. ✓ Существующий возвращается без изменений
3. ✓ Username обновляется при изменении
4. ✗ Неверный hash initData
5. ✗ Пустой initData
6. ✗ Отсутствует user в initData
7. ✓ Rate limit (опционально)
8. ✓ Дубликат tg_id вызывает IntegrityError

get_user_by_tg_id (3 теста):
1. ✓ Находит существующего
2. ✓ Возвращает None для несуществующего
3. ✗ Неверный tg_id (<0)

ban_user (6 тестов):
1. ✓ Админ банит пользователя
2. ✓ Админ разбанивает
3. ✗ Не-админ не может банить
4. ✗ Пользователь не найден
5. ✓ banned_at устанавливается
6. ✓ is_banned меняется

status checks (4 теста):
1. ✓ is_user_banned=True
2. ✓ is_user_admin=True
3. ✓ can_create_themes=False (banned)
4. ✓ search_users работает

stats (2 теста):
1. ✓ get_user_stats корректно
2. ✓ get_admin_users возвращает админов

Итого: 23+ тест-кейса, покрытие 90%+.

--------------------------------------------------
🧾 ПРИМЕРЫ КОНТРАКТОВ
--------------------------------------------------
Telegram webhook → get_or_create_user(db, init_data)
✅ User(id=42, tg_id=123456, username="@testuser", is_banned=False)

POST /admin/users/42/ban → ban_user(db, 42, True, admin_id=1)
✅ User(id=42, is_banned=True, banned_at="2026-04-13T16:45:00")

GET /users/tg/123456 → get_user_by_tg_id(db, 123456)
✅ 200 User(...) или 404

GET /admin/stats → get_user_stats(db)
✅ 200 {"total_users": 1250, "banned_users": 15, ...}

--------------------------------------------------
🚀 РЕКОМЕНДУЕМАЯ ФИНАЛЬНАЯ СТРУКТУРА
--------------------------------------------------
1. imports (SQLAlchemy, security, config)
2. TELEGRAM INITDATA валидация (verify_telegram_init_data)
3. private helpers (_extract_user_data, _update_user_profile)
4. main functions:
   - get_or_create_user
   - get_user_by_tg_id, get_user_by_id
   - ban_user
5. status checks (is_user_banned, is_user_admin, can_*)
6. search + stats (search_users, get_user_stats, get_admin_users)

--------------------------------------------------
💡 MVP vs PRODUCTION
--------------------------------------------------
MVP минимум (Неделя 2):
- get_or_create_user
- get_user_by_tg_id
- ban_user

Production (Неделя 3+):
+ get_user_by_id
+ is_user_banned, is_user_admin
+ search_users
+ get_user_stats
+ get_admin_users
+ rate limiting на создание

--------------------------------------------------
✅ ИТОГ
--------------------------------------------------
Users service — фундаментальный сервис проекта.
От него зависят themes, requests и bots.

Правильный поток:
Telegram WebApp → initData → Users service (валидация+создание) → Themes/Requests service → Bot notifications

Ключевые принципы:
1. Telegram initData валидируется ТОЛЬКО здесь
2. Все сервисы используют get_user_by_tg_id()
3. Статусные проверки (banned/admin) — чистые функции
4. ban_user логирует действия админов
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
