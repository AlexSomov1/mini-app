"""
⏳ BACKEND B: МОДЕЛЬ THEME (темы встреч)
==================================================
Модель темы встречи: "Матан в ауд.305, 15 марта 19:00"

🎯 ЦЕЛЬ: Хранить информацию о встрече + кто создал
📱 Frontend: список тем → деталь → заявка

📋 ПОЛЯ МОДЕЛИ (Backend B):
| Поле | Тип | Описание | Обязательно |
|------|-----|----------|-------------|
| id | Integer PK | Автоинкремент | ✅ |
| title | String(255) | "Матан с Петровым" | ✅ |
| description | Text | Подробности встречи | Нет |
| datetime | DateTime | 2026-03-15T19:00 | ✅ |
| location | String(255) | "ауд.305 СПбПУ" | ✅ |
| creator_id | FK User | Кто создал тему | ✅ |
| max_slots | Integer | Макс. участников (30) | Нет |

⏳ TODO Неделя 2 (Backend B):
1. SQLAlchemy модель с ForeignKey("user.id")
2. relationship creator=relationship("User")
3. requests=relationship("Request")
4. Index по datetime (поиск ближайших)
5. Pydantic ThemeCreate/ThemePublic

🧪 ТЕСТИРОВАНИЕ:
1. Theme(title="Матан", creator_id=123).save()
2. GET /themes → [{"id":1, "title":"Матан", "creator":{...}}]
3. 404 если creator_id не существует!

🚀 API ИСПОЛЬЗОВАНИЕ (app/api/themes.py):
POST /themes {"title":"Матан", "datetime":"2026-03-15T19:00"}
← Backend B проверит: current_user.is_banned == False
"""

from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy import ForeignKey
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.core.db import Base

class Theme(Base):
    __tablename__ = "theme"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    datetime = Column(DateTime, nullable=False, index = True)
    location = Column(String(255), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    max_slots = Column(Integer, nullable=True)

    creator = relationship("User")
    requests = relationship("Request", back_populates = "theme")
