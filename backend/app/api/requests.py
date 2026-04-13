"""
⏳ BACKEND C: API REQUESTS ROUTER
==================================================
/api/v1/requests/* — заявки на участие

🎯 ЦЕЛЬ: Студент → заявка → модератор approve → уведомление

📋 ЭНДПОИНТЫ (Backend C, Неделя 2):
| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| POST | /themes/{theme_id}/requests | Подать заявку | user |
| GET | /themes/{theme_id}/requests | Список заявок | creator |
| PATCH | /themes/{theme_id}/requests/{id} | Approve/Reject | creator |

⏳ TODO Backend C:
1. ApiRouter
2. POST: check !exists(user_id, theme_id)
3. PATCH: status="approved" → bot notification
4. max_slots=30 → auto-reject если заполнено

🧪 ТЕСТИРОВАНИЕ:
POST /api/v1/themes/1/requests → 201 {"status":"pending"}

PATCH /api/v1/themes/1/requests/5
{"status": "approved"} → уведомление user_id!

🔐 ПРАВА:
- POST: любой !banned user
- GET/PATCH: только creator темы
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.request import RequestCreate, RequestPublic, RequestModerate
from app.services import requests_service

router = APIRouter(prefix="/themes/{theme_id}/requests",
                   tags=["requests"])

@router.post("", response_model=RequestPublic)
async def create_request_endpoint(theme_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    request = await requests_service.create_request(db, theme_id, user_id)
    return request

@router.get("", response_model=list[RequestPublic])
async def get_request_endpoint(theme_id: int, db: AsyncSession = Depends(get_db)):
    request = await requests_service.get_requests_for_theme(db, theme_id)
    return request

@router.patch("/{id}", response_model=RequestPublic)
async def patch_request(request_id: int, data: RequestModerate, db: AsyncSession = Depends(get_db)):
    request = await requests_service.moderate_request(db, request_id, data.status)
    return request