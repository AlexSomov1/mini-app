"""
⏳ BACKEND B: THEME SCHEMAS
==================================================
Валидация данных темы встречи

📋 SCHEMAS (Backend B):
| Схема | Назначение | Поля |
|-------|------------|------|
| ThemeCreate | POST /themes | title, datetime, location |
| ThemePublic | GET /themes | id, title, creator, slots |
| ThemeListResponse | Список тем | themes[], total_count |

⏳ TODO Backend B:
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class ThemeCreate(BaseModel):
    title: str = Field(..., max_length=255, description="Название встречи")
    description: Optional[str] = Field(None, max_length=1000)
    datetime: datetime = Field(..., description="Дата и время встречи")
    location: str = Field(..., max_length=255, example="ауд.305 СПбПУ")
    max_slots: int = Field(30, ge=1, le=100)

    @validator("datetime")
    def future_date(cls, v):
        if v <= datetime.now():
            raise ValueError("Дата встречи должна быть в будущем")
        return v

class ThemePublic(BaseModel):
    id: int
    title: str
    description: Optional[str]
    datetime: datetime
    location: str
    creator: UserPublic  # Вложенная схема!
    max_slots: int
    requests_count: int = 0
    slots_available: int

    class Config:
        from_attributes = True

class ThemeListResponse(BaseModel):
    themes: list[ThemePublic]
    total_count: int
    has_more: bool
"""

from pydantic import BaseModel, Field, ConfigDict,field_validator
from datetime import datetime as dt
from datetime import timezone
from typing import Optional
from ..schemas.user import UserPublic

class ThemeCreate(BaseModel):
    title: str = Field(..., max_length=255, description="Название встречи")
    datetime: dt = Field(..., description="Дата и место встречи")
    location: str = Field(..., max_length=255)
    max_slots: int = Field(default = 30, ge = 1, le = 100)
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator('datetime')
    def check_datetime(cls, value):
        if value <= dt.now(timezone.utc):
            raise ValueError("Некорректная дата встречи")
        return value

class ThemePublic(BaseModel):
    id: int
    title: str
    creator: UserPublic
    datetime: dt
    location: str
    max_slots: int

    model_config = ConfigDict(from_attributes=True)

class ThemeListResponse(BaseModel):
    themes: list[ThemePublic]
    total_count: int

