PolyMeeting MiniApp

Telegram Mini App для организации встреч студентов СПбПУ.

Создавай темы встреч, отправляй заявки, получай уведомления. Полный цикл: бот → Mini App → Backend → БД.

Что делает приложение
1. Бот: `/start` → кнопка "Открыть Mini App"
2. Mini App: список тем, создание тем, заявки
3. Backend: API + бизнес-логика + уведомления
4. БД: пользователи, темы, заявки

Быстрый старт (2 команды)

Backend 
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Frontend 
cd frontend
npm install
npm run dev

Адреса:
Backend API: http://localhost:8000/docs
Frontend: http://localhost:5173
Бот: работает в Telegram

Структура проекта:
mini-app/
├── backend/                 # FastAPI + aiogram
│   ├── app/
│   │   ├── api/            # HTTP роутеры: /themes, /requests
│   │   ├── services/       # Бизнес-логика
│   │   ├── models/         # ORM модели БД
│   │   ├── core/           # config, БД, security
│   │   └── bots/           # Telegram бот
│   └── main.py
├── frontend/               # React + TypeScript
│   ├── src/
│   │   ├── api/           # HTTP клиенты
│   │   ├── pages/         # Экраны Mini App
│   │   └── hooks/         # useTelegram
│   └── package.json
├── infra/                  # Docker
└── docs/                   # Документация API

