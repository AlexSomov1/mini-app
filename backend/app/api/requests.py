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
1. APIRouter(tags=["requests"])
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
