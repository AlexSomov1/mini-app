```markdown
# PolyMeeting MiniApp 🚀

**Telegram Mini App для организации встреч студентов СПбПУ.**

Создавай темы встреч, отправляй заявки, получай уведомления через бота. Полный цикл: бот → Mini App → API → БД → уведомления.

[![Backend](https://img.shields.io/badge/Backend-FastAPI-blue?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Frontend](https://img.shields.io/badge/Frontend-React%2BTS-green?style=flat&logo=react)](https://react.dev)
[![Database](https://img.shields.io/badge/DB-SQLite-orange?style=flat&logo=sqlite)](https://sqlite.org)

## 🎯 Что делает приложение

```
1. 👤 /start в Telegram Bot → кнопка "Открыть Mini App"
2. 📱 Mini App: список тем, создание тем, заявки на участие  
3. 🔌 Backend API: обработка запросов, бизнес-логика
4. 💾 База данных: пользователи, темы, заявки
5. 🔔 Уведомления: "Вас приняли на встречу!"
```

## 🚀 Быстрый старт (2 команды)

### Backend (вкладка 1)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (вкладка 2)
```bash
cd frontend
npm install
npm run dev
```

**✅ Адреса:**
- **Backend API**: http://localhost:8000/docs ← Swagger документация
- **Frontend**: http://localhost:5173 ← React Mini App
- **Бот**: работает в Telegram

## 🏗️ Архитектура (4 слоя)

```
📱 PRESENTATION LAYER
├── Mini App (React + TypeScript)
└── Telegram Bot (aiogram 3.x)

🔌 API LAYER (FastAPI)
├── api/themes.py ← POST /themes, GET /themes
├── api/requests.py ← POST /themes/{id}/request
├── api/users.py ← GET /me профиль
└── api/admin.py ← бан пользователей

🧠 DOMAIN LAYER (Сервисы)
├── services/themes_service.py ← бизнес-логика тем
├── services/requests_service.py ← модерация заявок
└── services/users_service.py ← профили

💾 DATA LAYER (БД)
├── models/user.py ← tg_id, username, is_banned
├── models/theme.py ← title, datetime, location
├── models/request.py ← theme_id, user_id, status
└── core/db.py ← SQLAlchemy async
```

## 👥 Команда и роли

| Разработчик | Домен | Файлы |
|-------------|-------|-------|
| **Backend A** | Core + Users | `core/`, `models/user.py`, `api/users.py` |
| **Backend B** | Themes | `models/theme.py`, `api/themes.py`, `services/themes_service.py` |
| **Backend C** | Requests | `models/request.py`, `api/requests.py`, `services/requests_service.py` |
| **Backend D** | Bot + Admin | `bots/`, `api/admin.py`, уведомления |
| **Frontend 1** | Каркас | Telegram WebApp, навигация |
| **Frontend 2** | Экраны | Список тем, формы заявок |

## 📱 Telegram Bot — настройка

1. **@BotFather** → `/newbot`
2. **Название**: `PolyMeeting Bot`
3. **Username**: `polymeeting_bot`
4. **Скопируй BOT_TOKEN** в `backend/.env`:
```
BOT_TOKEN=7770000000:AAExxx_your_token_here
```

## 🛠️ Локальная разработка

### Git workflow
```bash
git checkout develop          # рабочая ветка
git pull origin develop       # обновить
git checkout -b feature/имя   # своя ветка
# код + тесты
git add . && git commit -m "feat: ..."
git push -u origin feature/имя
# Создай PR в develop
```

### Запуск (README для команды)
```bash
# Клонировать
git clone https://github.com/AlexSomov1/mini-app.git
cd mini-app

# Backend + Frontend = 2 команды (см. Быстрый старт)
```

## 📊 Статус проекта

| Компонент | Статус | Порт |
|-----------|--------|------|
| Backend API | ✅ Работает | 8000 |
| Frontend | ✅ React+Vite | 5173 |
| База данных | ⏳ Backend A | - |
| Telegram Bot | ⏳ Backend D | - |
| Docker | ⏳ В плане | - |

## 🚀 Дорожная карта (2 месяца)

```
Недели 1-4: MVP
✅ Неделя 1: Скелеты backend + frontend ✓
⏳ Неделя 2: Backend домены (A,B,C,D)
⏳ Неделя 3: Frontend экраны + интеграция
⏳ Неделя 4: MVP демо

Недели 5-8: Полировка
⏳ Фильтры, пагинация, чат заявок
⏳ Тесты 80% покрытие
⏳ Docker + продакшн деплой
⏳ Документация API
```

## 🧪 Тестирование

```bash
# Backend тесты
pytest tests/ -v

# Frontend тесты  
npm test
```

## 🤝 Как внести вклад

1. Форк → `git clone твоя-копия`
2. Ветка `feature/описание`
3. Код + тесты + линтер
4. PR в `develop` с ревью

## 📄 Лицензия

MIT © 2026 PolyMeeting Team
```

***

**Копируй целиком → вставь в README.md → сохрани → `git add . && git commit -m "docs: update README with full project info" && git push`**

**Этот README:**
✅ **Красивый** — бейджи, таблицы, эмодзи  
✅ **Полный** — вся информация для команды  
✅ **Понятный** — инструкции + роли + план  
✅ **Профессиональный** — GitHub на уровне стартапа  

**Команда будет в восторге! 🚀**

Источники
