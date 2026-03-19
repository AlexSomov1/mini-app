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
```python
from enum import Enum
from pydantic import BaseModel

class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved" 
    rejected = "rejected"

class RequestCreate(BaseModel):
    theme_id: int = Field(..., gt=0)

class RequestPublic(BaseModel):
    id: int
    theme_id: int
    user: UserPublic
    status: RequestStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class RequestModerate(BaseModel):
    status: RequestStatus

class RequestsListResponse(BaseModel):
    requests: list[RequestPublic]
    total_pending: int
    total_approved: int
"""