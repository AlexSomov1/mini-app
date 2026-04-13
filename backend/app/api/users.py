"""
✅ BACKEND A: API USERS ROUTER
==================================================
/api/v1/users/* — профиль пользователя Telegram

🎯 АВТОРИЗАЦИЯ: Telegram initDataUnsafe → get_or_create_user()

📋 ЭНДПОИНТЫ (Backend A, Неделя 2):
| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | /users/me | Текущий профиль | initData |
| POST | /users/ | Создать/обновить | initData |

⏳ TODO Backend A:
1. APIRouter(prefix="/api/v1/users", tags=["users"])
2. Depends(get_current_user) ← service.get_or_create_user(init_data)
3. Response: UserPublic (без tg_id в проде!)
4. 409 Conflict если duplicate tg_id

🧪 ТЕСТИРОВАНИЕ (Postman):
POST /api/v1/users
{
  "tg_id": 123456789,
  "username": "@student_spbpu",
  "full_name": "Иванов Иван"
}
→ 200 {"id":1, "username":"@student_spbpu"}

🔐 FRONTEND ВЫЗОВ (React):
const initData = Telegram.WebApp.initDataUnsafe;
const response = await api.post("/api/v1/users", initData);
const user = response.data; // UserPublic

🚀 ОШИБКИ:
- 400: invalid initData signature
- 409: user with tg_id already exists  
- 401: banned user
"""
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.user import UserCreate, UserPublic
from app.services import users_service

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/me", response_model=UserPublic)
async def get_me(tg_id: int, db: AsyncSession = Depends(get_db)):
    user = await users_service.get_user_by_tg_id(db=db, tg_id=tg_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_banned:
        raise HTTPException(status_code=403, detail="Юзер забанен")

    return user


@router.post("/", response_model=UserPublic)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await users_service.get_or_create_user(
        db=db, tg_id=data.tg_id, username=data.username, full_name=data.full_name
    )

    if user.is_banned:
        raise HTTPException(status_code=403, detail="Юзер забанен")

    return user


