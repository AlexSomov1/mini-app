"""
⏳ BACKEND C: REQUEST SCHEMAS
==================================================
Валидация заявок на участие

📋 SCHEMAS (Backend C):
| Схема | Назначение | Поля |
|-------|------------|------|
| RequestCreate | POST заявка | theme_id, user_id (авто) |
| RequestPublic | GET список | id, status, theme, user |
| RequestModerate | PATCH approve | status |

⏳ TODO Backend C:
"""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.theme import ThemePublic
from app.schemas.user import UserPublic


class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class RequestCreate(BaseModel):
    theme_id: int = Field(..., gt=0)

class RequestPublic(BaseModel):
    id: int
    status: RequestStatus
    theme_id: int
    user : UserPublic

    created_at: datetime

    class Config:
        from_attributes = True

class RequestModerate(BaseModel):
    status: RequestStatus


class RequestWithTheme(RequestPublic):
    theme: ThemePublic
