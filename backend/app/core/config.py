"""
🔧 НАСТРОЙКИ ПРИЛОЖЕНИЯ (Pydantic Settings)
==================================================
Чтение .env → pydantic объекты

✅ Backend A (Неделя 2):
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./app.db"
    bot_token: str
    admin_ids: List[int] = []
    secret_key: str = "CHANGE_ME"
    
    class Config:
        env_file = ".env"

settings = Settings()
print(settings.database_url)  # → engine

📋 ПЕРЕМЕННЫЕ .env:
DATABASE_URL=sqlite+aiosqlite:///./app.db
BOT_TOKEN=777000:AAExxx_your_token_here
ADMIN_IDS=123456789,987654321
SECRET_KEY=super-secret-change-in-production
"""
