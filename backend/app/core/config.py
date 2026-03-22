"""
🔧 НАСТРОЙКИ ПРИЛОЖЕНИЯ (Pydantic Settings)
==================================================
Чтение .env → pydantic объекты

📋 ПЕРЕМЕННЫЕ .env:
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./app.db"
    bot_token: str
    admin_ids: List[int] = []
    secret_key: str = "CHANGE_ME"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
print(settings.database_url)