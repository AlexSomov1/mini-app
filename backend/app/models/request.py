"""
⏳ BACKEND C: МОДЕЛЬ REQUEST (заявки на встречу)
==================================================
Модель заявки студента на участие в теме

🎯 ЦЕЛЬ: Подать заявку → модератор approve/reject → уведомление
📱 Frontend: кнопка "Записаться" → POST /themes/{id}/requests

📋 ПОЛЯ МОДЕЛИ (Backend C):
| Поле | Тип | Описание | Обязательно |
|------|-----|----------|-------------|
| id | Integer PK | Автоинкремент | ✅ |
| theme_id | FK Theme | На какую тему | ✅ |
| user_id | FK User | Кто подал | ✅ |
| status | Enum | pending/approved/rejected | ✅ |
| created_at | DateTime | Когда подал | ✅ |

⏳ TODO Неделя 2 (Backend C):
1. ForeignKey theme_id, user_id
2. unique(theme_id, user_id) ← 1 заявка/человек!
3. relationship theme=relationship("Theme"), user=relationship("User")
4. Pydantic RequestCreate, RequestPublic
5. max_requests_per_theme = 30 (validate в service)

🧪 ТЕСТИРОВАНИЕ:
1. Request(theme_id=1, user_id=123, status="pending").save()
2. UNIQUE constraint: 2 заявки от 1 user → 409 Conflict
3. PATCH status="approved" → уведомление в bots/

🚀 API ИСПОЛЬЗОВАНИЕ:
POST /themes/1/requests → 201 Created (status="pending")
PATCH /themes/1/requests/5 → {"status":"approved"} (admin only)
"""
from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.schemas.request import RequestStatus

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, autoincrement=True, primary_key=True)
    theme_id = Column(Integer, ForeignKey("theme.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("theme_id", "user_id"),)

    theme = relationship("Theme")
    user = relationship("User")

