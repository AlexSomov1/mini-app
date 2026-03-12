"""
🌐 FASTAPI API РОУТЕРЫ (APIRouter)
==================================================
Подключение в app/main.py:

from . import users, themes, requests, admin
app.include_router(users.router, prefix="/api/v1/users")

✅ СТАТУС Неделя 2:
- Backend A: /api/v1/users/me ✅ готово к разработке
- Backend B: /api/v1/themes ⏳ CRUD
- Backend C: /api/v1/requests ⏳ заявки
- Backend D: /api/v1/admin ⏳ модерация

📱 Swagger: http://localhost:8000/docs
🧪 Postman: backend/tests/postman_collection.json
"""
