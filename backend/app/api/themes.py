"""
✅ BACKEND B: API THEMES ROUTER (ПОЛНОЕ ОПИСАНИЕ)
==================================================
/api/v1/themes/* — API-роутер для тем встреч

🎯 ЦЕЛЬ ФАЙЛА:
Этот файл отвечает только за HTTP API для тем встреч.
Он не должен содержать бизнес-логику создания темы, проверки banned,
проверки прав creator/admin, работы с базой напрямую через select(),
подсчета слотов или сложной валидации данных.
Все это должно жить в themes_service и auth/dependencies.

Задача api/themes.py:
- описать HTTP-эндпоинты для CRUD операций по темам;
- принять query/path/body параметры;
- получить пользователя через Depends(get_current_user), если нужно;
- вызвать соответствующую функцию themes_service;
- вернуть response_model;
- корректно перевести бизнес-ошибки в HTTPException;
- не дублировать бизнес-логику из service.

Идеальная архитектура:
router → dependency/auth → themes_service → db

Если в этом файле появляются:
- ручные SQL-запросы через select(User) или select(Theme);
- ручное открытие AsyncSessionLocal();
- ручная логика creator/admin/banned;
- ручное создание Theme(...);
значит структура сломана, и код надо переносить в service/dependencies.

--------------------------------------------------
📦 ЗОНА ОТВЕТСТВЕННОСТИ API THEMES ROUTER
--------------------------------------------------
Файл api/themes.py отвечает за:

1. GET /api/v1/themes/
   - вернуть список тем;
   - поддерживать limit, offset, future_only.

2. POST /api/v1/themes/
   - создать новую тему;
   - доступно только авторизованному и не забаненному пользователю.

3. GET /api/v1/themes/{theme_id}
   - вернуть детали одной темы.

4. DELETE /api/v1/themes/{theme_id}
   - удалить тему;
   - доступно только creator темы или admin.

5. При расширении:
   - PATCH /api/v1/themes/{theme_id}
   - GET /api/v1/themes/{theme_id}/requests
   - GET /api/v1/themes/my/list

Но для MVP недели 2 достаточно:
- GET /
- POST /
- GET /{theme_id}
- DELETE /{theme_id}

--------------------------------------------------
📋 ОСНОВНЫЕ ЭНДПОИНТЫ ФАЙЛА
--------------------------------------------------
| Метод | Путь | Назначение | Auth | Response |
|-------|------|------------|------|----------|
| GET | / | Список тем | public | list[ThemePublic] или ThemeListResponse |
| POST | / | Создать тему | user | ThemePublic |
| GET | /{theme_id} | Детали темы | public | ThemeDetail |
| DELETE | /{theme_id} | Удалить тему | creator/admin | 204 No Content или MessageResponse |

--------------------------------------------------
🧱 ОБЯЗАТЕЛЬНЫЕ ИМПОРТЫ
--------------------------------------------------
Файл обычно должен использовать:

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.user import User
from app.schemas.theme import ThemeCreate, ThemePublic, ThemeDetail, ThemeListResponse
from app.services import themes_service
from app.api.dependencies.auth import get_current_user, get_optional_user, get_admin_user

Если get_optional_user пока не нужен, его можно не использовать.
Главное:
- БД должна приходить через Depends(get_db);
- текущий пользователь должен приходить через Depends(get_current_user);
- роутер не должен сам создавать session или искать текущего user.

FastAPI обычно строит роутеры именно через APIRouter + Depends,
а БД и auth передаются как зависимости, а не создаются вручную в теле функции. [web:295][web:312][web:318]

--------------------------------------------------
🚀 APIRouter ФАЙЛА
--------------------------------------------------
Роутер должен быть объявлен так:

router = APIRouter(
    prefix="/api/v1/themes",
    tags=["themes"]
)

Дополнительно можно сразу описать responses:
router = APIRouter(
    prefix="/api/v1/themes",
    tags=["themes"],
    responses={
        400: {"description": "Bad request"},
        403: {"description": "Forbidden"},
        404: {"description": "Theme not found"},
    }
)

Важно:
если prefix уже "/api/v1/themes",
то внутри эндпоинтов надо писать:
- "/"
- "/{theme_id}"
а не "/themes" и не "/themes/{id}".

Иначе получится дублирование пути:
"/api/v1/themes/themes". [web:296][web:265]

--------------------------------------------------
✅ GET /
--------------------------------------------------
Назначение:
вернуть список тем с пагинацией и фильтрацией.

Правильная сигнатура:

@router.get("/", response_model=ThemeListResponse)
async def list_themes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    future_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    items, total = await themes_service.get_themes(
        db=db,
        limit=limit,
        offset=offset,
        future_only=future_only,
    )
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

Упрощенный MVP-вариант:
response_model=list[ThemePublic]
и просто return await themes_service.get_themes(...)

Но если вы уже хотите нормальную пагинацию, лучше сразу возвращать:
- items
- total
- limit
- offset
- has_more (опционально)

Что важно:
- limit и offset должны быть Query параметрами;
- public доступ, без авторизации;
- роутер не должен писать select(Theme) напрямую;
- логика future_only должна быть в service.

Ошибки:
- 400 invalid pagination
- 500 db/service error

--------------------------------------------------
✅ POST /
--------------------------------------------------
Назначение:
создать новую тему.

Доступ:
только авторизованный пользователь, не забаненный.

Правильная сигнатура:

@router.post("/", response_model=ThemePublic, status_code=201)
async def create_theme_route(
    theme_ ThemeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await themes_service.create_theme(
        db=db,
        creator=current_user,
        theme_data=theme_data,
    )

Что важно:
- функция роутера не должна называться create_theme, если уже импортирован service.create_theme;
  лучше create_theme_route;
- current_user должен приходить через Depends(get_current_user);
- banned-проверка должна жить в dependency или service;
- datetime validation должна жить в service и/или schema;
- роутер только принимает ThemeCreate и вызывает service.

Ответ:
- 201 Created
- ThemePublic

Ошибки:
- 400 invalid datetime / invalid business rule
- 403 banned user
- 401 unauthorized
- 422 invalid request body

--------------------------------------------------
✅ GET /{theme_id}
--------------------------------------------------
Назначение:
вернуть детали одной темы.

Правильная сигнатура:

@router.get("/{theme_id}", response_model=ThemeDetail)
async def get_theme_by_id(
    theme_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    theme = await themes_service.get_theme_by_id(db=db, theme_id=theme_id)
    return theme

Важно:
- path parameter должен называться theme_id и в path, и в функции одинаково;
- не использовать "/{id}" если в функции параметр theme_id;
- роутер не должен делать SQL напрямую;
- если детали темы должны содержать slots info,
  это либо делает service.get_theme_detail(...),
  либо response собирается из нескольких service функций.

Ошибки:
- 404 theme not found
- 400 invalid theme_id

--------------------------------------------------
✅ DELETE /{theme_id}
--------------------------------------------------
Назначение:
удалить тему.

Доступ:
только creator темы или admin.

Правильная сигнатура:

@router.delete("/{theme_id}", status_code=204)
async def delete_theme_route(
    theme_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await themes_service.delete_theme(
        db=db,
        theme_id=theme_id,
        current_user=current_user,
        is_admin=current_user.is_admin,
    )
    return None

Альтернатива:
вернуть JSON:
{"detail": "Theme deleted"}

Но для REST чище 204 No Content.

Что важно:
- не делать get_me(session);
- не использовать заглушку пользователя;
- не открывать AsyncSessionLocal() вручную;
- не удалять тему напрямую через db.delete(...) в роутере;
- право creator/admin должно проверяться в service.

Ошибки:
- 403 forbidden
- 404 theme not found
- 401 unauthorized

--------------------------------------------------
❌ ЧТО НЕПРАВИЛЬНО В ТЕКУЩЕМ ВАРИАНТЕ
--------------------------------------------------
Следующие моменты в текущем коде неверны:

1. router уже имеет prefix="/api/v1/themes",
   но POST объявлен как @router.post("/themes")
   и DELETE как @router.delete("/themes/{id}").
   Это создает неправильные маршруты:
   /api/v1/themes/themes
   вместо
   /api/v1/themes/

2. GET /{id} и параметр theme_id не совпадают по имени.
   В FastAPI имя path параметра должно совпадать с именем аргумента функции. [web:312][web:313]

3. Роутер вручную открывает session:
   async with AsyncSessionLocal() as session:
   Вместо этого должен использоваться:
   db: AsyncSession = Depends(get_db)
   Это стандартный паттерн зависимости для БД. [web:317][web:318]

4. В файле есть get_current_user-заглушка с хардкодом tg_id.
   Это не считается реализованной авторизацией.

5. Импортируется get_me из другого router-файла:
   from app.api.users import get_me
   Так делать нельзя.
   Эндпоинт одного роутера не должен использоваться как dependency другого роутера.
   Нужна отдельная dependency-функция auth слоя.

6. Локальные имена функций конфликтуют с service imports:
   create_theme, delete_theme.
   Это приводит к путанице и потенциальным багам.

7. Нет response_model.
   Значит наружу уходит то, что вернул service/ORM,
   а не зафиксированный публичный контракт API.

--------------------------------------------------
📤 RESPONSE MODELS
--------------------------------------------------
Роутер должен использовать response_model для каждого endpoint,
чтобы:
- документировать API;
- валидировать ответ;
- скрывать лишние поля;
- сделать ответы стабильными для фронта. [web:296]

Рекомендуемые схемы:

1. ThemeCreate
   Входная схема POST /
   Поля:
   - title
   - description
   - datetime
   - location
   - max_slots (опционально)

2. ThemePublic
   Краткое публичное представление темы
   Поля:
   - id
   - title
   - description
   - datetime
   - location
   - creator_id или creator summary
   - created_at

3. ThemeDetail
   Детальное представление
   Поля:
   - все из ThemePublic
   - requests_count
   - approved_count
   - slots_available
   - is_full

4. ThemeListResponse
   Если делаете пагинацию объектом:
   - items: list[ThemePublic]
   - total: int
   - limit: int
   - offset: int
   - has_more: bool (опционально)

--------------------------------------------------
⚠️ ОБРАБОТКА ОШИБОК
--------------------------------------------------
Роутер должен корректно маппить ошибки service слоя в HTTPException,
если у проекта еще нет глобальных exception handlers.

Типичные случаи:
- BadRequestError → 400
- ForbiddenError → 403
- NotFoundError → 404
- ConflictError → 409

FastAPI обычно использует HTTPException для клиентских ошибок,
а код и описание можно дополнительно документировать через responses. [web:294][web:305]

Пример:
@router.post(
    "/",
    response_model=ThemePublic,
    status_code=201,
    responses={
        400: {"description": "Invalid theme data"},
        403: {"description": "User is banned"},
    },
)

--------------------------------------------------
🧪 ЧТО ДОЛЖНО БЫТЬ ПРОТЕСТИРОВАНО
--------------------------------------------------
Минимальные тесты для api/themes.py:

1. GET / success
   - возвращает список тем

2. GET / with query params
   - limit, offset, future_only работают

3. POST / success
   - авторизованный пользователь создает тему
   - ответ 201

4. POST / banned user
   - ожидаем 403

5. POST / invalid datetime
   - ожидаем 400 или 422

6. GET /{theme_id} success
   - возвращает одну тему

7. GET /{theme_id} not found
   - ожидаем 404

8. DELETE /{theme_id} by creator
   - 204 success

9. DELETE /{theme_id} by admin
   - 204 success

10. DELETE /{theme_id} forbidden
   - 403

--------------------------------------------------
📁 РЕКОМЕНДУЕМАЯ ФИНАЛЬНАЯ СТРУКТУРА ФАЙЛА
--------------------------------------------------
1. imports
2. router = APIRouter(...)
3. GET /
4. POST /
5. GET /{theme_id}
6. DELETE /{theme_id}

Важно:
не добавлять внутрь файла:
- AsyncSessionLocal() manual usage
- fake current user
- SQL for user/theme lookup
- business validations

--------------------------------------------------
💡 MVP vs PRODUCTION
--------------------------------------------------
MVP минимум:
- router = APIRouter(prefix="/api/v1/themes", tags=["themes"])
- GET /
- POST /
- GET /{theme_id}
- DELETE /{theme_id}
- Depends(get_db)
- Depends(get_current_user) для POST/DELETE
- response_model
- корректные 400/403/404 ответы

Production:
+ ThemeListResponse с total/has_more
+ ThemeDetail со slots info
+ PATCH /{theme_id}
+ глобальные exception handlers
+ логирование действий creator/admin
+ отдельные dependencies для optional user/admin

--------------------------------------------------
✅ ИТОГ
--------------------------------------------------
api/themes.py считается сделанным правильно только если:

1. У него корректный APIRouter(prefix="/api/v1/themes").
2. Внутри маршрутов нет дублирования "/themes".
3. Все БД-сессии приходят через Depends(get_db), а не через AsyncSessionLocal().
4. current_user приходит через Depends(get_current_user), а не через заглушку.
5. Роутер не содержит бизнес-логики themes_service.
6. Все ответы типизированы через response_model.
7. Path/query параметры названы корректно и совпадают с декораторами.
8. Ошибки сервиса превращаются в корректные HTTP статусы.

Главная мысль:
api/themes.py должен быть тонким CRUD-роутером,
а не местом, где вручную пишутся fake auth, SQL и логика доступа.
"""


from fastapi import APIRouter
from sqlalchemy import select
from ..models.theme import Theme
from ..models.user import User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from ..core.db import AsyncSessionLocal, get_db
from ..schemas.theme import ThemeCreate
from ..services.themes_service import create_theme, get_theme, get_themes, delete_theme
from app.api.users import get_me
from fastapi import Depends

router = APIRouter(prefix="/api/v1/themes", tags=["themes"])

#получение текущего пользователя (пока что заглушка)
async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    result = await db.execute(
        select(User).where(User.tg_id == 12377331)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            tg_id=12377331,
            username="test",
            full_name="test",
            is_banned=False,
            is_admin=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user

@router.get("/", summary="Получить список всех тем")
async def get_all_themes():
  async with AsyncSessionLocal() as session:
    result = await get_themes(session)

    return result

@router.get("/{id}", summary = "Получить детали темы по id")
async def get_theme_data(theme_id: int):
  async with AsyncSessionLocal() as session:
    result = await get_theme(session, theme_id)

  return result

@router.post("/themes", summary = "Опубликовать тему")
async def create_theme_api(themeToCreate: ThemeCreate):
  async with AsyncSessionLocal() as session:
    user = await get_current_user(session)
    result = await create_theme(session, user, themeToCreate)

  return result

@router.delete("/themes/{id}", summary = "Удалить тему")
async def delete_theme_api(theme_id: int):
  async with AsyncSessionLocal() as session:
    user = await get_current_user(session)
    await delete_theme(session, theme_id, user)

  return "deleted"
