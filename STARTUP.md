# КАК ЗАПУСКАТЬ ПРОЕКТ

## 1. БЭКЕНД

```bash
cd mini-app/backend
source .venv/bin/activate
uvicorn main:app --reload
```

Запускается на http://localhost:8000
Swagger документация: http://localhost:8000/docs

---

## 2. ФРОНТЕНД

```bash
cd mini-app/frontend
npm run dev
```

Запускается на http://localhost:5173

---

## 3. ТУННЕЛИ (чтобы работало в Telegram)

Фронтенд — через ngrok (URL не меняется пока сессия активна):
```bash
ngrok http 5173
```

Бэкенд — через localhost.run (URL меняется каждый раз при перезапуске!):
```bash
ssh -R 80:localhost:8000 nokey@localhost.run
```

---

## 4. ГДЕ МЕНЯТЬ ССЫЛКИ

Каждый раз когда перезапускаешь localhost.run — URL бэкенда меняется.
Нужно обновить его в двух местах:

**Фронтенд** — `frontend/src/App.tsx`, строка:
```typescript
const BACKEND_URL = 'https://XXXXX.lhr.life';
```

**Бэкенд CORS** — `backend/main.py`, строка:
```python
allow_origins=["http://localhost:5173", "https://tendrilly-chantay-inceptively.ngrok-free.dev", "https://XXXXX.lhr.life"],
```

---

## 5. СОЗДАТЬ ПОЛЬЗОВАТЕЛЯ ВРУЧНУЮ ЧЕРЕЗ ТЕРМИНАЛ

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"tg_id": 123456789, "username": "test_user", "full_name": "Иван Иванов"}'
```

Проверить что записалось в БД:
```bash
sqlite3 backend/app.db "SELECT * FROM users;"
```

Удалить тестового пользователя:
```bash
sqlite3 backend/app.db "DELETE FROM users WHERE tg_id = 123456789;"
```
