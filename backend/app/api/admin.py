"""
⏳ BACKEND D: API ADMIN ROUTER (куратор СПбПУ)
==================================================
/api/v1/admin/* — модерация (только ADMIN_IDS)

🎯 ЦЕЛЬ: Куратор банит спамеров + статистика

📋 ЭНДПОИНТЫ (Backend D, Неделя 3):
| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| PATCH | /users/{user_id}/ban | Забанить/разбанить | admin |
| GET | /stats | Статистика тем/заявок | admin |
| POST | /broadcast | Рассылка всем | admin |

⏳ TODO Backend D:
1. APIRouter(prefix="/api/v1/admin", tags=["admin"])
2. Depends(is_admin) ← tg_id в settings.ADMIN_IDS
3. PATCH ban: user.is_banned = True/False
4. GET /stats → {"users":100, "themes":50, "requests":200}

🧪 ТЕСТИРОВАНИЕ (ADMIN_TOKEN):
PATCH /api/v1/admin/users/123/ban {"is_banned": true}
→ 200 {"message": "User banned"}

🔐 АДМИНЫ (.env ADMIN_IDS):
ADMIN_IDS=[123456789, 987654321]  # tg_id кураторов
"""
