"""
✅ BACKEND A: API USERS ROUTER (ПОЛНОЕ ОПИСАНИЕ)
==================================================
/api/v1/users/* — роутер профиля пользователя Telegram WebApp

🎯 ЦЕЛЬ ФАЙЛА:
Этот файл отвечает только за API-слой пользователей.
Здесь не должно быть бизнес-логики создания пользователя, проверки hash,
работы с Telegram initData, банов и поиска по БД напрямую.
Все это должно жить в users_service и зависимостях auth/dependencies.

Задача api/users.py:
- описать HTTP-эндпоинты;
- принять входные данные;
- вызвать users_service;
- вернуть response_model;
- преобразовать бизнес-ошибки в HTTPException;
- подключить зависимости Depends(get_db), Depends(get_current_user), Depends(get_admin_user).

Идеальная архитектура:
router → dependency/auth → service → db

Если в этом файле появляется логика:
- сравнения hash,
- db.execute(select(...)),
- ручного создания User(...),
- проверки дубликатов,
- сложной проверки banned/admin,
значит архитектура нарушена и часть кода надо переносить в service/dependencies.

--------------------------------------------------
📦 ЗОНА ОТВЕТСТВЕННОСТИ API USERS ROUTER
--------------------------------------------------
Файл api/users.py отвечает за:

1. GET /api/v1/users/me
   - вернуть текущий профиль авторизованного пользователя.

2. POST /api/v1/users/
   - создать или обновить пользователя из Telegram initData.

3. GET /api/v1/users/tg/{tg_id}
   - получить пользователя по Telegram ID (обычно только для admin).

4. POST /api/v1/users/{user_id}/ban
   - забанить или разбанить пользователя (только admin).

5. GET /api/v1/users/stats
   - вернуть статистику пользователей (только admin).

6. При необходимости:
   - GET /api/v1/users/{user_id}
   - GET /api/v1/users/search
   - GET /api/v1/users/admins

Но для MVP недели 2 достаточно:
- GET /me
- POST /

--------------------------------------------------
📋 ОСНОВНЫЕ ЭНДПОИНТЫ ФАЙЛА
--------------------------------------------------
| Метод | Путь | Назначение | Auth | Response |
|-------|------|------------|------|----------|
| GET | /me | Текущий пользователь | Telegram initData | UserPublic |
| POST | / | Создать/обновить пользователя | Telegram initData | UserPublic |
| GET | /tg/{tg_id} | Найти по tg_id | admin | UserPublic |
| POST | /{user_id}/ban | Бан/разбан | admin | UserPublic |
| GET | /stats | Статистика пользователей | admin | UserStats |

--------------------------------------------------
🧱 ОБЯЗАТЕЛЬНЫЕ ИМПОРТЫ
--------------------------------------------------
Файл обычно должен использовать:

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.user import UserPublic, UserBanAction, UserStats
from app.models.user import User
from app.services import users_service
from app.api.dependencies.auth import get_current_user, get_admin_user

Если у вас еще нет app.api.dependencies.auth, его нужно создать.
Именно dependency должна извлекать Telegram initData и отдавать готового User.
Такой подход соответствует обычной модульной структуре FastAPI с APIRouter и dependencies. [web:295][web:298][web:306]

--------------------------------------------------
🚀 APIRouter ФАЙЛА
--------------------------------------------------
Роутер должен быть объявлен так:

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"]
)

Дополнительно можно описать общие responses:
router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
    }
)

FastAPI позволяет задавать prefix, tags, dependencies и responses
на уровне роутера, чтобы не дублировать конфигурацию в каждом эндпоинте. [web:296][web:295]

--------------------------------------------------
🔐 АВТОРИЗАЦИЯ И DEPENDENCIES
--------------------------------------------------
Ключевая идея этого файла:
он НЕ должен вручную валидировать Telegram initData внутри каждого эндпоинта.

Вместо этого должны существовать зависимости:

1. get_current_user
   - принимает Telegram initData;
   - вызывает users_service.get_or_create_user(...);
   - проверяет, что пользователь не забанен;
   - возвращает готовый объект User.

2. get_admin_user
   - использует get_current_user;
   - дополнительно проверяет admin права;
   - если прав нет — бросает HTTP 403.

Пример логики dependency:

async def get_current_user(
    init_ Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await users_service.get_or_create_user(db=db, init_data=init_data)
    if users_service.is_user_banned(user):
        raise HTTPException(status_code=403, detail="User is banned")
    return user

async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not users_service.is_user_admin(current_user, settings.ADMIN_TG_IDS):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

ВАЖНО:
если dependency уже проверяет banned/admin,
то в роутерах не надо повторять эти проверки еще раз.

--------------------------------------------------
✅ GET /me
--------------------------------------------------
Назначение:
вернуть текущий профиль пользователя, полученного через Telegram initData.

Правильная сигнатура:

@router.get("/me", response_model=UserPublic)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

Что важно:
- НЕ принимать tg_id через query;
- НЕ искать пользователя вручную через db;
- НЕ валидировать hash прямо тут;
- НЕ создавать пользователя вручную прямо тут.

Вся авторизация должна происходить в Depends(get_current_user).

Ответ:
- 200 OK + UserPublic

Ошибки:
- 400 invalid initData
- 403 user is banned
- 500 service/db failure

--------------------------------------------------
✅ POST /
--------------------------------------------------
Назначение:
создать или обновить пользователя из Telegram initData.

Этот эндпоинт нужен, если фронтенд отдельно вызывает регистрацию/синхронизацию профиля.
По сути, это "upsert user from Telegram".

Правильная сигнатура примерно такая:

@router.post("/", response_model=UserPublic, status_code=200)
async def create_or_update_user(
    init_ Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
):
    user = await users_service.get_or_create_user(db=db, init_data=init_data)
    if users_service.is_user_banned(user):
        raise HTTPException(status_code=403, detail="User is banned")
    return user

Что важно:
- вход — это НЕ UserCreate с tg_id/username/full_name;
- вход — это именно Telegram initData целиком;
- users_service сам решает: создать пользователя или обновить уже существующего;
- роут просто возвращает UserPublic.

Ошибки:
- 400 invalid initData signature
- 403 banned user
- 409 duplicate/unique conflict
- 500 db error

--------------------------------------------------
❌ ЧТО НЕПРАВИЛЬНО В ТЕКУЩЕМ ВАРИАНТЕ
--------------------------------------------------
Следующий вариант считается неполным и архитектурно неверным:

@router.get("/me")
async def get_me(tg_id: int, db: AsyncSession = Depends(get_db)):

Почему это неправильно:
1. tg_id в query не подтверждает личность пользователя;
2. любой клиент может подставить чужой tg_id;
3. это ломает Telegram auth flow;
4. get_me должен получать current_user из dependency.

Следующий вариант тоже неверен:

@router.post("/")
async def create_user( UserCreate, db: AsyncSession = Depends(get_db)):

Почему:
1. users_service ожидает init_data, а не отдельные поля;
2. hash Telegram не проверяется;
3. фронтенд не должен вручную собирать внутреннюю схему UserCreate вместо initData;
4. это обходит Telegram trust model.

--------------------------------------------------
✅ GET /tg/{tg_id}
--------------------------------------------------
Назначение:
админский поиск пользователя по Telegram ID.

Этот эндпоинт не обязателен для MVP,
но полезен для админки и отладки.

Пример сигнатуры:

@router.get("/tg/{tg_id}", response_model=UserPublic)
async def get_user_by_tg_id(
    tg_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    user = await users_service.get_user_by_tg_id(db=db, tg_id=tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

Что делает:
- доступен только админу;
- получает tg_id из path;
- вызывает service;
- если пользователя нет — 404.

--------------------------------------------------
✅ POST /{user_id}/ban
--------------------------------------------------
Назначение:
бан или разбан пользователя администратором.

Для него лучше иметь отдельную входную схему, например:

class UserBanAction(BaseModel):
    is_banned: bool

Пример сигнатуры:

@router.post("/{user_id}/ban", response_model=UserPublic)
async def ban_user(
    user_id: int,
    payload: UserBanAction,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    user = await users_service.ban_user(
        db=db,
        user_id=user_id,
        is_banned=payload.is_banned,
        admin_id=admin_user.id,
    )
    return user

Ошибки:
- 403 admin required
- 404 user not found
- 400 cannot ban admin / invalid action

ВАЖНО:
логика бана живет в users_service, а не здесь.

--------------------------------------------------
✅ GET /stats
--------------------------------------------------
Назначение:
получить агрегированную статистику пользователей.

Пример сигнатуры:

@router.get("/stats", response_model=UserStats)
async def get_users_stats(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    return await users_service.get_user_stats(db=db)

Этот эндпоинт нужен только для admin dashboard.

--------------------------------------------------
📤 RESPONSE MODELS
--------------------------------------------------
Роутер обязан использовать response_model.

Это важно потому что response_model:
- документирует ответ в OpenAPI;
- валидирует ответ;
- скрывает лишние поля;
- позволяет не отдавать чувствительные данные наружу. [web:296]

Минимум должны быть такие схемы:

1. UserPublic
   Публичный пользовательский профиль.
   Пример полей:
   - id
   - username
   - first_name
   - last_name
   - is_banned (опционально, если нужно фронту)
   - created_at

   В проде обычно НЕ стоит отдавать:
   - tg_id
   - внутренние admin поля
   - service metadata

2. UserStats
   Пример:
   - total_users
   - banned_users
   - active_users
   - admins
   - created_last_7d

3. UserBanAction
   Входная схема для POST /{user_id}/ban:
   - is_banned: bool

--------------------------------------------------
⚠️ ОБРАБОТКА ОШИБОК
--------------------------------------------------
Роутер должен маппить ошибки service-слоя в HTTPException.

Если в проекте нет кастомных exceptions handlers,
можно делать это прямо в файле.

Примеры:
- ValueError / InvalidTelegramInitData → 400 Bad Request
- ConflictError → 409 Conflict
- ForbiddenError → 403 Forbidden
- NotFoundError → 404 Not Found

FastAPI рекомендует поднимать HTTPException для клиентских ошибок,
а для явного описания этих ответов можно использовать responses в декораторах. [web:294][web:305][web:307]

Пример:
@router.post(
    "/",
    response_model=UserPublic,
    responses={
        400: {"description": "Invalid Telegram initData"},
        403: {"description": "User is banned"},
        409: {"description": "User conflict"},
    },
)

--------------------------------------------------
🧪 ЧТО ДОЛЖНО БЫТЬ ПРОТЕСТИРОВАНО
--------------------------------------------------
Минимальные тесты для api/users.py:

1. GET /me success
   - валидный initData
   - возвращает UserPublic

2. GET /me banned user
   - dependency возвращает banned user
   - ожидаем 403

3. GET /me invalid initData
   - hash невалидный
   - ожидаем 400

4. POST / success
   - создается/обновляется user
   - response = UserPublic

5. POST / duplicate conflict
   - service поднимает conflict
   - ожидаем 409

6. GET /tg/{tg_id} admin success
   - admin получает пользователя

7. GET /tg/{tg_id} forbidden for non-admin
   - ожидаем 403

8. POST /{user_id}/ban success
   - admin банит пользователя

9. GET /stats success
   - admin получает статистику

--------------------------------------------------
📁 РЕКОМЕНДУЕМАЯ ФИНАЛЬНАЯ СТРУКТУРА ФАЙЛА
--------------------------------------------------
1. imports
2. router = APIRouter(...)
3. GET /me
4. POST /
5. admin endpoints:
   - GET /tg/{tg_id}
   - POST /{user_id}/ban
   - GET /stats

Если проект пока маленький, можно оставить только:
- GET /me
- POST /

Но даже в MVP они должны работать через Telegram initData,
а не через tg_id query param.

--------------------------------------------------
💡 MVP vs PRODUCTION
--------------------------------------------------
MVP минимум:
- router = APIRouter(prefix="/api/v1/users", tags=["users"])
- GET /me через Depends(get_current_user)
- POST / через initData → users_service.get_or_create_user(...)
- response_model=UserPublic
- корректные 400/403/409 ошибки

Production:
+ admin endpoints
+ responses в декораторах
+ отдельные схемы UserStats и UserBanAction
+ глобальные exception handlers
+ dependency get_admin_user
+ логирование admin действий

--------------------------------------------------
✅ ИТОГ
--------------------------------------------------
api/users.py считается сделанным правильно только если:

1. Он использует APIRouter с prefix="/api/v1/users".
2. GET /me получает current_user через Depends(get_current_user).
3. POST / принимает Telegram initData, а не UserCreate с ручными полями.
4. Он не содержит бизнес-логики и SQL-запросов напрямую.
5. Все чувствительные поля скрываются через UserPublic.
6. Ошибки service-слоя переводятся в корректные HTTP-коды.
7. banned/admin проверки вынесены в dependencies или users_service.

Главная мысль:
api/users.py должен быть тонким роутером,
а не местом, где вручную реализуется логика Telegram авторизации и работы с пользователем.
"""

from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.user import UserCreate, UserPublic
from app.services import users_service

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/me", response_model=UserPublic)
async def get_me(tg_id: int, db: AsyncSession = Depends(get_db)):
    user = await users_service.get_user_by_tg_id(db=db, tg_id=tg_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_banned:
        raise HTTPException(status_code=403, detail="Юзер забанен")

    return user


@router.post("/", response_model=UserPublic)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await users_service.get_or_create_user(
        db=db, tg_id=data.tg_id, username=data.username, full_name=data.full_name
    )

    if user.is_banned:
        raise HTTPException(status_code=403, detail="Юзер забанен")

    return user


