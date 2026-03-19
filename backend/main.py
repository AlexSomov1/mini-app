from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

"""
🎯 ГЛАВНЫЙ ФАЙЛ FASTAPI ПРИЛОЖЕНИЯ
==================================================
Точка входа: uvicorn app.main:app --reload

✅ Backend A,B,C,D: подключайте роутеры здесь!

📋 TODO Неделя 2 (обязательно):
1. app.include_router(users.router, prefix="/users", tags=["users"])
2. app.include_router(themes.router, prefix="/themes", tags=["themes"])
3. app.include_router(requests.router, prefix="/requests", tags=["requests"])
4. app.include_router(admin.router, prefix="/admin", tags=["admin"])
5. CORSMiddleware для localhost:5173 (React dev)
6. lifespan=create_all_tables() on startup

🧪 ТЕСТИРОВАНИЕ:
$ curl http://localhost:8000/ 
> {"message": "PolyMeeting API v1.0 🚀"}

$ curl http://localhost:8000/docs 
> Swagger UI с вашими эндпоинтами

🔒 CORS для Frontend:
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

📈 МЕТРИКИ КАЧЕСТВА (GitHub Actions):
- pytest --cov=app/ --cov-report=html >= 80%
- ruff check . == 0 ошибок
- mypy app/ == типизация 100%

🚀 ПРИМЕР ПОДКЛЮЧЕНИЯ РОУТЕРА (Backend A):
from .api import users
app.include_router(users.router, prefix="/users", tags=["users"])

📱 ИНТЕГРАЦИЯ С FRONTEND (неделя 3):
Frontend вызовет: axios.get("http://localhost:8000/users/me")
← вернёт UserPublic из Telegram initData
"""


app = FastAPI(
    title="PolyMeeting MiniApp API",
    description="API для Telegram Mini App",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "PolyMeeting API работает! 🚀"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/docs")
async def docs():
    return {"docs": "http://localhost:8000/docs", "openapi": "http://localhost:8000/openapi.json"}
