"""
🚀 POLYMEETING FASTAPI APPLICATION v1.0
==================================================
Telegram Mini App для организации встреч СПбПУ

🎯 ЦЕЛЬ: Backend API + Telegram Bot в одной кодовой базе
📱 Frontend: localhost:5173 (React + TS)
🔌 Backend: localhost:8000 (FastAPI + SQLAlchemy async)
🤖 Bot: @polymeeting_bot (aiogram 3.10 webhook)

📂 СТРУКТУРА ПРОЕКТА:
├── app/           ← FastAPI приложение (этот файл)
│   ├── models/    ← SQLAlchemy ORM (User/Theme/Request)
│   ├── api/       ← Роутеры FastAPI (/users, /themes)
│   ├── services/  ← Бизнес-логика (get_or_create_user)
│   ├── schemas/   ← Pydantic валидация
│   └── core/      ← DB, Config, Security
├── bots/          ← Aiogram Telegram Bot
├── tests/         ← 80% покрытие pytest
└── utils/         ← Логгер, валидаторы

🚀 ЗАПУСК:
$ cd backend
$ python -m venv venv && source venv/bin/activate
$ pip install -r requirements.txt
$ uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

✅ Swagger: http://localhost:8000/docs
✅ Bot webhook: https://your-ngrok-url/webhook

📅 ДОРОЖНАЯ КАРТА (8 недель):
✅ Неделя 1: Скелеты backend/frontend
⏳ Неделя 2: Модели + API Users/Themes/Requests  
⏳ Неделя 3: Frontend интеграция + Bot /start
⏳ Неделя 4: MVP демо СПбПУ

👥 КОМАНДА:
- Backend A: User модель + DB
- Backend B: Theme CRUD
- Backend C: Request модерация  
- Backend D: Bot + Admin API
- Frontend 1,2: React UI + Telegram WebApp

GitHub: github.com/AlexSomov1/mini-app
"""
