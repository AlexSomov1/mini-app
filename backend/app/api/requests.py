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

router = APIRouter(prefix="/themes/{theme_id}/requests",
                   tags=["requests"])

fake_db = [
    {"user_id": 1, "theme_id": 1}, ]
request_id_seq = 1

"""1 endpoint: CREATE REQUEST with fake db"""
@router.post("")
async def create_request(theme_id: int, user_id: int):
    global request_id_seq
    for r in fake_db:
        if r["user_id"] == user_id and r["theme_id"] == theme_id:
            raise HTTPException(
                status_code=400,
                detail="already exist"
            )
    request = {
        "id" : request_id_seq,
        "user_id" : user_id,
        "theme_id": theme_id,
        "status" : "pending"
    }
    request_id_seq += 1
    fake_db.append(request)
    return request

"""2 endpoint: GET REQUESTS with fake db"""
@router.get("")
async def get_request(theme_id: int):
    result = [r for r in fake_db if r["theme_id"] == theme_id]
    if result == []:
        return {"not found request"}
    return result

"""3 endpoint: GET REQUESTS with fake db"""
@router.patch("/{id}")
async def patch_request(theme_id: int, request_id: int, status: str):
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="invalid status")
    for r in fake_db:
        if r["id"] == request_id and r["theme_id"] == theme_id:
            r["status"] = status
            return r
    raise HTTPException(status_code=400, detail="request not found")
"""TODO ADD NOTIFY USERS"""