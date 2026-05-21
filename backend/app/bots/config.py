from pydantic_settings import BaseSettings
from typing import List
from app.core.config import settings as app_settings

class BotConfig(BaseSettings):
    BOT_TOKEN: str
    WEBAPP_URL: str
    # Берем админов из основного конфига, если есть
    ADMIN_IDS: List[int] = app_settings.admin_ids if hasattr(app_settings, "admin_ids") else []

    class Config:
        env_file = ".env"
        extra = "ignore"

config = BotConfig()