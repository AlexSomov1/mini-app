"""
✅ BACKEND C: REQUESTS SERVICE (ПОЛНОЕ ОПИСАНИЕ)
==================================================
Бизнес-логика заявок на встречи: подача, модерация, список заявок,
проверка дубликатов, слоты, уведомления и права доступа.

🎯 ЦЕЛЬ ФАЙЛА:
Requests service — центральная точка бизнес-логики работы с заявками.
Здесь должны быть ВСЕ правила:
- кто и когда может подать заявку;
- как проверять дубликаты;
- как считать слоты;
- кто может модерировать заявки;
- когда отправлять уведомления;
- какие статусы заявок допустимы.

API-слой (app/api/requests.py) только вызывает service функции
и преобразует их результат в HTTP-ответы.

--------------------------------------------------
📦 ЗОНА ОТВЕТСТВЕННОСТИ REQUESTS SERVICE
--------------------------------------------------
Requests service отвечает за:

1. Подачу заявки на тему (с проверками).
2. Модерацию заявки (approve/reject/pending).
3. Получение списка заявок по теме (для модератора).
4. Получение заявки пользователя по теме (для проверки статуса).
5. Проверку прав модератора.
6. Подсчет заявок по теме/статусу.
7. Отправку уведомлений через Bot service.
8. Бизнес-валидацию:
   - нет дубликатов заявок от пользователя;
   - тема существует и не удалена;
   - есть свободные слоты;
   - пользователь не забанен;
   - модератор имеет право на заявку.

--------------------------------------------------
📋 ОСНОВНЫЕ ФУНКЦИИ ФАЙЛА
--------------------------------------------------
| Функция | Назначение | Кто вызывает |
|---------|------------|--------------|
| create_request | Подать заявку на тему | api/requests.py POST /themes/{id}/requests |
| moderate_request | Изменить статус заявки + уведомить | api/requests.py PATCH /requests/{id} |
| get_requests_for_theme | Список заявок по теме | api/requests.py GET /themes/{id}/requests |
| get_user_request_for_theme | Заявка пользователя по теме | api/requests.py GET /themes/{id}/my-request |
| count_requests_by_status | Статистика заявок по статусам | внутреннее |
| can_moderate_request | Проверка прав модератора | внутреннее |
| notify_request_status_changed | Уведомление пользователя | внутреннее |

--------------------------------------------------
🧱 ПРЕДПОЛАГАЕМЫЕ ЗАВИСИМОСТИ
--------------------------------------------------
from sqlalchemy import select, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Tuple

from app.models.request import Request, RequestStatus
from app.models.theme import Theme  
from app.models.user import User
from app.services.bots_service import notify_user  # уведомления
from app.services.themes_service import get_theme_by_id

--------------------------------------------------
🧠 БИЗНЕС-ПРАВИЛА ЗАЯВОК
--------------------------------------------------
1. Один пользователь — одна заявка на тему (уникальность theme_id + user_id).
2. Забаненный пользователь не может подавать заявки.
3. Тема должна существовать и не быть удаленной.
4. Максимум 30 approved заявок на тему (max_slots).
5. Статусы заявок: pending → approved/rejected.
6. Модерировать может только:
   - создатель темы;
   - администратор.
7. При смене статуса отправлять уведомление.
8. Заявки на прошедшие темы не принимаются.
9. Список заявок видит только модератор темы.

--------------------------------------------------
✅ RequestStatus ENUM (рекомендуется)
--------------------------------------------------
class RequestStatus(Enum):
    PENDING = "pending"    # ожидает модерации
    APPROVED = "approved"  # принят
    REJECTED = "rejected"  # отклонен

--------------------------------------------------
🧩 ПОЛНАЯ СИГНАТУРА ФУНКЦИЙ
--------------------------------------------------

1. CREATE REQUEST
async def create_request(
    db: AsyncSession,
    theme_id: int,
    user: User
) -> Request:

2. MODERATE REQUEST  
async def moderate_request(
    db: AsyncSession,
    request_id: int,
    new_status: RequestStatus,
    moderator: User
) -> Request:

3. LIST FOR THEME
async def get_requests_for_theme(
    db: AsyncSession,
    theme_id: int,
    moderator: User
) -> List[Request]:

4. USER REQUEST STATUS
async def get_user_request_for_theme(
    db: AsyncSession,
    theme_id: int,
    user_id: int
) -> Optional[Request]:

--------------------------------------------------
✅ ПОЛНОЕ ПОВЕДЕНИЕ create_request()
--------------------------------------------------
Функция create_request() обязана:

1. Проверить пользователя: user.is_banned == False
2. Найти тему: await get_theme_by_id(db, theme_id)
3. Проверить тему:
   - theme.datetime > datetime.now() (не прошедшая)
   - theme.is_deleted == False (если есть soft delete)
4. Проверить дубликат: EXISTS(theme_id, user_id)
5. Проверить слоты: approved_requests < theme.max_slots
6. Создать заявку:
   request = Request(
       theme_id=theme_id,
       user_id=user.id,
       status=RequestStatus.PENDING
   )
7. db.add(request) → await db.commit() → await db.refresh(request)
8. Вернуть ORM объект Request

Ошибки:
- ForbiddenError("User is banned")
- NotFoundError("Theme not found") 
- ConflictError("Request already exists")
- BadRequestError("Theme has passed or is full")

--------------------------------------------------
✅ ПОЛНОЕ ПОВЕДЕНИЕ moderate_request()
--------------------------------------------------
Функция moderate_request() обязана:

1. Найти заявку: await db.get(Request, request_id, options=[selectinload(Request.user, Request.theme)])
2. Проверить права: await can_moderate_request(db, request.theme_id, moderator)
3. Проверить статус: new_status in [PENDING, APPROVED, REJECTED]
4. Проверить изменение: new_status != request.status (опционально)
5. Обновить статус: request.status = new_status
6. Сохранить: await db.commit()
7. Отправить уведомление:
   if new_status != RequestStatus.PENDING:
       message = f"Ваша заявка {'принята' if approved else 'отклонена'}"
       await notify_user(request.user.tg_id, message, theme_title=request.theme.title)
8. Вернуть обновленную заявку

Ошибки:
- NotFoundError("Request not found")
- ForbiddenError("Not authorized to moderate")
- BadRequestError("Invalid status")

--------------------------------------------------
✅ ПОЛНОЕ ПОВЕДЕНИЕ get_requests_for_theme()
--------------------------------------------------
Функция обязана:

1. Найти тему: await get_theme_by_id(db, theme_id)
2. Проверить права: await can_moderate_theme(db, theme_id, moderator)
3. Получить заявки:
   stmt = select(Request).where(
       Request.theme_id == theme_id
   ).options(
       selectinload(Request.user),
       selectinload(Request.theme)
   ).order_by(Request.created_at.desc())
4. Вернуть список ORM объектов

Ошибки:
- NotFoundError("Theme not found")
- ForbiddenError("Not authorized to view requests")

--------------------------------------------------
✅ SUPPORT ФУНКЦИИ
--------------------------------------------------

1. count_requests_by_status
async def count_requests_by_status(
    db: AsyncSession,
    theme_id: int
) -> Dict[str, int]:
Возвращает:
{
    "pending": 3,
    "approved": 25, 
    "rejected": 2,
    "total": 30
}

2. get_theme_requests_stats
async def get_theme_requests_stats(
    db: AsyncSession,
    theme_id: int,
    max_slots: int = 30
) -> Dict:
Возвращает:
{
    "approved_count": 25,
    "pending_count": 3,
    "total_requests": 28,
    "slots_available": 5,
    "is_full": True,
    "can_accept_more": False
}

3. can_moderate_request
async def can_moderate_request(
    db: AsyncSession,
    request_id: int,
    moderator: User
) -> bool:
Проверяет: модератор = creator темы ИЛИ admin.

--------------------------------------------------
🔄 ТРАНЗАКЦИИ
--------------------------------------------------
create_request и moderate_request работают с транзакциями:

async def create_request(...):
    try:
        # проверки
        request = Request(...)
        db.add(request)
        await db.commit()
        await db.refresh(request)
        return request
    except Exception:
        await db.rollback()
        raise

async def moderate_request(...):
    try:
        # проверки + update
        await db.commit()
        # уведомление
        return request
    except Exception:
        await db.rollback()
        raise

--------------------------------------------------
🧪 ПОЛНЫЙ СПИСOK ТЕСТОВ (test_requests_service.py)
--------------------------------------------------
create_request (7 тестов):
1. ✓ success: валидная заявка
2. ✗ banned user
3. ✗ duplicate request  
4. ✗ theme full (30+ approved)
5. ✗ past theme datetime
6. ✗ non-existing theme
7. ✗ deleted theme

moderate_request (8 тестов):
1. ✓ creator approves
2. ✓ creator rejects
3. ✓ admin approves  
4. ✗ non-moderator
5. ✗ invalid status
6. ✓ notification sent (approved)
7. ✗ notification not sent (pending)
8. ✗ no notification on same status

get_requests_for_theme (4 теста):
1. ✓ creator sees requests
2. ✗ non-moderator forbidden
3. ✓ empty list
4. ✓ with user/theme preload

get_user_request_for_theme (3 теста):
1. ✓ user has request
2. ✓ user has no request (None)
3. ✗ theme not found

stats functions (3 теста):
1. ✓ count_requests_by_status
2. ✓ get_theme_requests_stats
3. ✓ slots calculation

Итого: 25+ тест-кейсов, покрытие 85%+.

--------------------------------------------------
🧾 ПРИМЕРЫ КОНТРАКТОВ
--------------------------------------------------
POST /themes/5/requests → create_request(db, 5, user)
✅ 201 Request(id=42, status="pending", ...)

PATCH /requests/42 {"status": "approved"} → moderate_request(db, 42, APPROVED, moderator)  
✅ 200 Request(id=42, status="approved", ...)

GET /themes/5/requests → get_requests_for_theme(db, 5, moderator)
✅ 200 [Request(...), Request(...)]

GET /themes/5/my-request → get_user_request_for_theme(db, 5, user.id)
✅ 200 Request(...) или 404 null

--------------------------------------------------
🚀 РЕКОМЕНДУЕМАЯ ФИНАЛЬНАЯ СТРУКТУРА
--------------------------------------------------
1. imports
2. кастомные исключения (если нет глобальных)
3. private helpers (_check_slots_available, _send_notification)
4. main functions (create_request, moderate_request, get_requests_for_theme)
5. user helpers (get_user_request_for_theme)
6. stats (count_requests_by_status, get_theme_requests_stats)
7. permissions (can_moderate_request)

--------------------------------------------------
💡 MVP vs PRODUCTION
--------------------------------------------------
MVP минимум (Неделя 2):
- create_request
- moderate_request  
- get_requests_for_theme

Production (Неделя 3+):
+ get_user_request_for_theme
+ count_requests_by_status  
+ get_theme_requests_stats
+ can_moderate_request
+ notify_request_status_changed

--------------------------------------------------
✅ ИТОГ
--------------------------------------------------
Requests service — самая сложная часть бизнес-логики вашего проекта.
Здесь пересекаются права доступа, слоты, уведомления, статусы и проверки.
Весь этот код должен быть здесь, а НЕ в роутерах.

Правильный поток:
Frontend → API (валидация схем) → Service (бизнес-правила) → DB (данные)
"""
from typing import Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from datetime import datetime

from app.models.request import Request
from app.models.user import User
from app.models.theme import Theme
from app.schemas.request import RequestStatus
from app.services.themes_service import get_theme


async def create_request(db: AsyncSession, theme_id: int, user: User) -> Request:
    try:
        if user.is_banned:
            raise HTTPException(status_code=403, detail="User is banned")

        theme = await get_theme(db, theme_id)

        if theme.datetime <= datetime.now():
            raise HTTPException(status_code=400, detail="Theme has already passed")

        duplicate_stmt = select(Request).where(
            Request.theme_id == theme_id,
            Request.user_id == user.id
        )
        existing = (await db.execute(duplicate_stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="Request already exists")

        slots_stmt = select(func.count()).where(
            Request.theme_id == theme_id,
            Request.status == RequestStatus.approved
        )
        approved_count = (await db.execute(slots_stmt)).scalar()
        if approved_count + 1 >= theme.max_slots:
            raise HTTPException(status_code=400, detail="Theme is full")

        request = Request(
            theme_id=theme_id,
            user_id=user.id,
            status=RequestStatus.pending
        )
        db.add(request)
        await db.commit()

        # Перезагружаем с явным selectinload — иначе lazy loading упадёт в async
        stmt = select(Request).where(Request.id == request.id).options(
            selectinload(Request.user)
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

async def count_requests_by_status(db: AsyncSession, theme_id: int) -> Dict[str, int]:
    stmt = (
        select(Request.status, func.count())
        .where(Request.theme_id == theme_id)
        .group_by(Request.status)
    )
    rows = (await db.execute(stmt)).all()
    counts = {status: count for status, count in rows}
    pending = counts.get(RequestStatus.pending, 0)
    approved = counts.get(RequestStatus.approved, 0)
    rejected = counts.get(RequestStatus.rejected, 0)
    return {
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "total": pending + approved + rejected,
    }

async def get_theme_requests_stats(db: AsyncSession, theme_id: int, max_slots: int = 30) -> Dict:
    counts = await count_requests_by_status(db, theme_id)
    approved = counts["approved"]
    rejected = counts["rejected"]
    total = counts["total"]

    slots_available = max_slots - approved
    is_full = slots_available <= 0
    return {
        "approved_count": approved,
        "rejected_count": rejected,
        "total_requests": total,
        "slots_available": slots_available,
        "is_full": is_full,
        "can_accept_more" : not is_full,
    }

async def can_moderate_request(db: AsyncSession, request_id: int, moderator: User) -> bool:
    stmt = select(Request).where(Request.id == request_id).options(
        selectinload(Request.theme)
    )
    request = (await db.execute(stmt)).scalar_one_or_none()
    if request is None:
        return False

    is_creator = request.theme.creator_id == moderator.id
    is_admin = moderator.is_admin

    return is_creator or is_admin

async def moderate_request(db: AsyncSession, request_id: int, new_status: RequestStatus, moderator: User ) -> Request:
    try:
        stmt = select(Request).where(Request.id == request_id).options(
            selectinload(Request.user),
            selectinload(Request.theme)
        )
        request = (await db.execute(stmt)).scalar_one_or_none()

        if request is None:
            raise HTTPException(status_code=404, detail="Request not found")

        allowed = await can_moderate_request(db, request_id, moderator)
        if not allowed:
            raise HTTPException(status_code=403, detail="Not authorized to moderate")

        request.status = new_status
        await db.commit()
    # TODO: Отправить уведомление юзеру о модерации заявки
        # if new_status != RequestStatus.pending:
        #     accepted = new_status == RequestStatus.approved
        #     message = f"Ваша заявка {'принята' if accepted else 'отклонена'}"
        #     await notify_user(request.user.tg_id, message, theme_title=request.theme.title)

        return request
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_requests_for_theme(db: AsyncSession, theme_id: int, moderator: User) -> List[Request]:
    theme = await get_theme(db, theme_id)

    if theme.creator_id != moderator.id and not moderator.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view requests")

    stmt = (
        select(Request)
        .where(Request.theme_id == theme_id)
        .options(
            selectinload(Request.user),
            selectinload(Request.theme)
        )
        .order_by(Request.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_user_requests(db: AsyncSession, user_id: int) -> List[Request]:
    stmt = (
        select(Request)
        .where(Request.user_id == user_id)
        .options(
            selectinload(Request.user),
            selectinload(Request.theme).selectinload(Theme.creator),
        )
        .order_by(Request.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_user_request_for_theme(db: AsyncSession, theme_id: int, user_id: int) -> Optional[Request]:
    stmt = (
        select(Request)
        .where(
            Request.theme_id == theme_id,
            Request.user_id == user_id
        )
        .options(
            selectinload(Request.user),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
