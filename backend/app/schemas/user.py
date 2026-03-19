"""
✅ BACKEND A: USER SCHEMAS (Pydantic)
==================================================
Валидация Telegram initData → User модель

📋 SCHEMAS (Backend A, Неделя 2):
| Схема | Назначение | Поля |
|-------|------------|------|
| UserCreate | POST /users (вход) | tg_id, username?, full_name |
| UserPublic | GET /users/me (выход) | id, username, full_name, is_banned |
| UserUpdate | PATCH /users/{id} | username?, full_name? |

⏳ TODO Backend A:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    tg_id: int = Field(..., gt=0, description="Telegram ID")
    username: Optional[str] = Field(None, max_length=32)
    full_name: str = Field(..., max_length=255)

class UserPublic(BaseModel):
    id: int
    tg_id: int
    username: Optional[str]
    full_name: str
    is_banned: bool
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=32)
    full_name: Optional[str] = Field(None, max_length=255)
"""