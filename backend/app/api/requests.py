"""
✅ BACKEND C: API REQUESTS ROUTER (ПОЛНОЕ ОПИСАНИЕ)
==================================================
/api/v1/themes/{theme_id}/requests/* — заявки на участие в теме

🎯 ЦЕЛЬ ФАЙЛА:
HTTP API для подачи заявок, просмотра и модерации заявок на тему.
Роутер отвечает только за маршруты, параметры и вызов service.
Бизнес-логика (проверка дубликатов, слоты, права creator, уведомления бота)
живет в requests_service.

Задача api/requests.py:
- маршрутизация /api/v1/themes/{theme_id}/requests/*
- валидация path/query/body параметров
- получение current_user через Depends()
- вызов requests_service
- response_model + HTTP статусы
- перевод service ошибок в HTTPException

--------------------------------------------------
📦 ЗОНА ОТВЕТСТВЕННОСТИ
--------------------------------------------------
Файл отвечает за:

1. POST /api/v1/themes/{theme_id}/requests/
   - подать заявку на участие
   - доступ: любой !banned user

2. GET /api/v1/themes/{theme_id}/requests/
   - список заявок темы
   - доступ: creator темы

3. PATCH /api/v1/themes/{theme_id}/requests/{request_id}
   - approve/reject заявки
   - доступ: creator темы

--------------------------------------------------
📋 ОСНОВНЫЕ ЭНДПОИНТЫ
--------------------------------------------------
| Метод | Путь | Назначение | Auth | Response |
|-------|------|------------|------|----------|
| POST | / | Подать заявку | user | RequestPublic (201) |
| GET | / | Список заявок | creator | list[RequestPublic] |
| PATCH | /{request_id} | Модерация | creator | RequestPublic |

--------------------------------------------------
🧱 ОБЯЗАТЕЛЬНЫЕ ИМПОРТЫ
--------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.db import get_db
from app.models.user import User
from app.schemas.request import RequestCreate, RequestPublic, RequestModerate
from app.services import requests_service
from app.api.dependencies.auth import get_current_user

--------------------------------------------------
🚀 APIRouter (ПРАВИЛЬНЫЙ)
--------------------------------------------------
router = APIRouter(
    prefix="/api/v1/themes",
    tags=["requests"]
)

ВНИМАНИЕ:
prefix НЕ может содержать path-параметры!
Правильно: prefix="/api/v1/themes"
theme_id передается через Path(...) в каждом эндпоинте.

НЕПРАВИЛЬНО:
router = APIRouter(prefix="/themes/{theme_id}/requests") ❌

--------------------------------------------------
✅ POST / (Подать заявку)
--------------------------------------------------
Назначение:
пользователь подает заявку на участие в теме.

Правильная сигнатура:

@router.post("/{theme_id}/requests/", 
             response_model=RequestPublic, 
             status_code=status.HTTP_201_CREATED)
async def create_request(
    theme_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request = await requests_service.create_request(
        db=db, 
        theme_id=theme_id, 
        user=current_user
    )
    return request

Что делает service.create_request():
- проверяет существование темы
- проверяет !user.is_banned  
- проверяет !exists(user_id, theme_id)
- проверяет available_slots > 0
- создает Request(status="pending")
- возвращает RequestPublic

Ошибки (service поднимает):
- 404 Theme not found
- 403 User is banned
- 409 Request already exists
- 403 Theme is full (max_slots)

--------------------------------------------------
✅ GET / (Список заявок)
--------------------------------------------------
Назначение:
creator темы смотрит список заявок.

Правильная сигнатура:

@router.get("/{theme_id}/requests/", response_model=List[RequestPublic])
async def list_requests(
    theme_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    requests = await requests_service.get_requests_for_theme(
        db=db, 
        theme_id=theme_id, 
        viewer_user=current_user
    )
    return requests

Что делает service:
- проверяет существование темы
- проверяет current_user == theme.creator_id
- возвращает все заявки темы (pending + approved + rejected)

Ошибки:
- 404 Theme not found
- 403 Access denied (not creator)

--------------------------------------------------
✅ PATCH /{request_id} (Модерация)
--------------------------------------------------
Назначение:
creator approve/reject заявку.

Правильная сигнатура:

@router.patch("/{theme_id}/requests/{request_id}", 
              response_model=RequestPublic)
async def moderate_request(
    theme_id: int = Path(..., gt=0),
    request_id: int = Path(..., gt=0),
    moderation_ RequestModerate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request = await requests_service.moderate_request(
        db=db,
        theme_id=theme_id,
        request_id=request_id,
        status=moderation_data.status,
        moderator_user=current_user
    )
    return request

RequestModerate схема:
class RequestModerate(BaseModel):
    status: Literal["approved", "rejected"]

Что делает service.moderate_request():
- проверяет существование request_id и принадлежность theme_id
- проверяет current_user == theme.creator_id
- обновляет request.status
- если "approved" → отправляет Telegram уведомление пользователю
- возвращает RequestPublic

Ошибки:
- 404 Request or Theme not found
- 403 Access denied (not creator)
- 400 Invalid status transition
- 409 Cannot approve (slots full)

--------------------------------------------------
❌ ЧТО НЕПРАВИЛЬНО В ТЕКУЩЕМ КОДЕ
--------------------------------------------------
1. ❌ prefix="/themes/{theme_id}/requests"
   Правильно: prefix="/api/v1/themes"

2. ❌ POST принимает user_id: int в аргументах
   Правильно: current_user = Depends(get_current_user)

3. ❌ Нет проверки прав creator для GET/PATCH
   Правильно: current_user в каждом эндпоинте + service проверка

4. ❌ PATCH не передает theme_id в service
   Правильно: service.moderate_request(db, theme_id, request_id, status)

5. ❌ Нет уведомлений бота при approve
   Правильно: requests_service.moderate_request() отправляет уведомление

6. ❌ Нет проверки max_slots
   Правильно: service проверяет available_slots > 0

--------------------------------------------------
📤 RESPONSE MODELS
--------------------------------------------------
1. RequestCreate (не используется в роутере, только в service)
   - user_id, theme_id (внутренние)

2. RequestPublic
   - id, theme_id, user_id, status, created_at, approved_at
   - НЕ отдавать чувствительные данные

3. RequestModerate (вход для PATCH)
   - status: Literal["approved", "rejected"]

--------------------------------------------------
🔐 ПРАВА ДОСТУПА (service уровень)
--------------------------------------------------
service.requests_service проверяет:

POST create_request():
- !user.is_banned
- theme exists
- !request_exists(user_id, theme_id) 
- theme.available_slots > 0

GET list_requests():
- viewer_user.id == theme.creator_id

PATCH moderate_request():
- moderator_user.id == theme.creator_id
- request.theme_id == theme_id
- валидный переход статуса

--------------------------------------------------
🧪 ТЕСТИРОВАНИЕ
--------------------------------------------------
1. POST /themes/1/requests → 201 {"status": "pending"}

2. POST duplicate → 409 "Request already exists"

3. POST theme full → 403 "No slots available"

4. GET /themes/1/requests (creator) → [{"id":1,"status":"pending"}]

5. GET /themes/1/requests (not creator) → 403

6. PATCH /themes/1/requests/1 {"status":"approved"} → уведомление user!

7. PATCH wrong theme_id → 404

8. PATCH not creator → 403

--------------------------------------------------
📁 ФИНАЛЬНАЯ СТРУКТУРА ФАЙЛА
--------------------------------------------------
1. imports
2. router = APIRouter(prefix="/api/v1/themes", tags=["requests"])
3. POST /{theme_id}/requests/
4. GET /{theme_id}/requests/  
5. PATCH /{theme_id}/requests/{request_id}

--------------------------------------------------
✅ ИТОГОВЫЕ КРИТЕРИИ ГОТОВНОСТИ
--------------------------------------------------
api/requests.py готов когда:

✅ prefix="/api/v1/themes" (без path params)
✅ Все эндпоинты используют Depends(get_db) + Depends(get_current_user)
✅ theme_id: Path(...) в каждом эндпоинте
✅ POST НЕ принимает user_id вручную
✅ GET/PATCH проверяют creator права через service  
✅ PATCH отправляет bot notification при approve
✅ response_model для всех эндпоинтов
✅ Корректные 400/403/404/409 ошибки
✅ service делает все проверки (slots, duplicates, rights)

Главная идея:
роутер — тонкий слой маршрутизации,
вся бизнес-логика (проверки прав, уведомления, слоты) в service.
"""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.request import RequestCreate, RequestPublic, RequestModerate
from app.services import requests_service

router = APIRouter(prefix="/themes/{theme_id}/requests",
                   tags=["requests"])

@router.post("", response_model=RequestPublic)
async def create_request_endpoint(theme_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    request = await requests_service.create_request(db, theme_id, user_id)
    return request

@router.get("", response_model=list[RequestPublic])
async def get_request_endpoint(theme_id: int, db: AsyncSession = Depends(get_db)):
    request = await requests_service.get_requests_for_theme(db, theme_id)
    return request

@router.patch("/{id}", response_model=RequestPublic)
async def patch_request(request_id: int, data: RequestModerate, db: AsyncSession = Depends(get_db)):
    request = await requests_service.moderate_request(db, request_id, data.status)
    return request