"""
⏳ BACKEND B: API THEMES ROUTER (CRUD)
==================================================
/api/v1/themes/* — создание/список тем встреч

🎯 ЦЕЛЬ: Студент создаёт тему → другие подают заявки

📋 ЭНДПОИНТЫ (Backend B, Неделя 2):
| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | /themes | Список тем (?limit=10) | public |
| POST | /themes | Создать тему | user |
| GET | /themes/{id} | Детали темы | public |
| DELETE | /themes/{id} | Удалить (creator/admin) | creator |

⏳ TODO Backend B:
1. APIRouter(prefix="/api/v1/themes", tags=["themes"])
2. GET /themes?limit=10&offset=0&future_only=true
3. POST /themes (ThemeCreate + current_user)
4. validate: !user.is_banned, datetime > now()

🧪 ТЕСТИРОВАНИЕ:
GET /api/v1/themes → [{"id":1,"title":"Матан","datetime":"2026-03-15T19:00"}]

POST /api/v1/themes 
{
  "title": "Матан с Петровым",
  "datetime": "2026-03-15T19:00",
  "location": "ауд.305"
}
→ 201 {"id":1,...}

🔐 ПРАВА ДОСТУПА:
- GET: все студенты
- POST: только !is_banned
- DELETE: creator_id == current_user.id ИЛИ admin
"""
