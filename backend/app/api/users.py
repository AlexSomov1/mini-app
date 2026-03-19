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
