"""
⏳ BACKEND C: REQUESTS SERVICE
==================================================
Логика заявок + уведомлений

📋 ФУНКЦИИ (Backend C):
| Функция | Описание |
|---------|----------|
| create_request | Подать заявку (!duplicate) |
| moderate_request | Approve/Reject + notify |
| get_requests_for_theme | Список для модератора |

⏳ TODO Неделя 2:
async def create_request(db, theme_id: int, user: User) -> Request:
    if await exists(db, theme_id, user.id): raise HTTPConflict
    if theme.requests_count >= 30: raise HTTPBadRequest
    request = Request(theme_id=theme_id, user_id=user.id, status="pending")
    # notify bot? await moderate_request(request.id, "auto_pending")

async def moderate_request(db, request_id: int, status: str):
    request = await db.get(Request, request_id)
    request.status = status
    if status == "approved":
        await bots.notify_user(request.user.tg_id, "Вас приняли!")
"""

from app.models.request import Request
from app.models.user import User
from app.schemas.request import RequestStatus
from sqlalchemy import select, func
from fastapi import HTTPException
from app.models.theme import Theme


async def exists(db, theme_id: int, user_id: int) -> bool:
    result = await db.execute(
        select(Request).where(
            Request.theme_id == theme_id,
            Request.user_id == user_id)
    )
    return result.scalar() is not None

async def create_request(db, theme_id: int, user_id: int) -> Request:
    if await exists(db, theme_id, user_id):
        raise HTTPException(status_code=409, detail="request already exists")

    if Theme is None:
        raise HTTPException(status_code=400, detail="theme is full")

    if Theme.max_slots is not None:
        count_result = await db.execute(
            select(func.count()).where(
                Request.theme_id == theme_id,
                Request.status == RequestStatus.approved
            )
        )
        count = count_result.scalar()
        if count >= Theme.max_slots:
            raise HTTPException(status_code=400, detail="theme is full")

    request = Request(theme_id=theme_id, user_id=user_id, status="pending")
    db.add(request)
    await db.commit()
    return request

async def moderate_request(db, request_id: int, status: RequestStatus) -> Request:
    request = await db.get(Request, request_id)
    if request is None: raise HTTPException(status_code=404, detail="request not found")
    request.status = status
    # TODO: Добавить оповещение пользователей
    #if status == "approved":
        #await bots.notify_user(request.user.tg_id, "Вас приняли!")

    await db.commit()
    await db.refresh(request)
    return request

async def get_requests_for_theme(db, theme_id: int):
    result = await db.execute(
        select(Request).where(Request.theme_id == theme_id)
    )
    return result.scalars().all()