"""
✅ BACKEND D: API ADMIN ROUTER (ПОЛНОЕ ОПИСАНИЕ)
==================================================
/api/v1/admin/* — админский роутер для куратора/модератора

🎯 ЦЕЛЬ ФАЙЛА:
Этот файл отвечает только за HTTP API админских действий.
Он не должен содержать прямую бизнес-логику банов, подсчета статистики,
массовой рассылки, SQL-запросов к таблицам пользователей/тем/заявок
или ручную проверку tg_id в каждом эндпоинте.
Все это должно жить в admin_service, users_service и auth/dependencies.

Задача api/admin.py:
- описать админские HTTP-эндпоинты;
- подключить зависимость Depends(get_admin_user);
- принять path/body/query параметры;
- вызвать service-функции;
- вернуть response_model;
- перевести service-ошибки в HTTPException;
- не дублировать auth/business logic внутри роутера.

Идеальная архитектура:
router → admin dependency → admin_service / users_service → db

Если в этом файле появляются:
- select(User), select(Theme), select(Request) напрямую;
- ручное открытие AsyncSessionLocal();
- проверки current_user.tg_id in ADMIN_IDS внутри каждого эндпоинта;
- ручное изменение user.is_banned в роутере;
- цикл рассылки ботом по пользователям прямо в endpoint;
значит архитектура нарушена, и эту логику надо переносить в service/dependencies.

--------------------------------------------------
📦 ЗОНА ОТВЕТСТВЕННОСТИ API ADMIN ROUTER
--------------------------------------------------
Файл api/admin.py отвечает за:

1. PATCH /api/v1/admin/users/{user_id}/ban
   - забанить или разбанить пользователя;
   - доступно только admin.

2. GET /api/v1/admin/stats
   - получить агрегированную статистику по системе;
   - доступно только admin.

3. POST /api/v1/admin/broadcast
   - отправить массовую рассылку пользователям;
   - доступно только admin.

4. При расширении:
   - GET /api/v1/admin/users
   - GET /api/v1/admin/themes
   - GET /api/v1/admin/requests
   - PATCH /api/v1/admin/themes/{theme_id}/hide
   - GET /api/v1/admin/logs

Но для MVP недели 3 достаточно:
- PATCH /users/{user_id}/ban
- GET /stats
- POST /broadcast

--------------------------------------------------
📋 ОСНОВНЫЕ ЭНДПОИНТЫ ФАЙЛА
--------------------------------------------------
| Метод | Путь | Назначение | Auth | Response |
|-------|------|------------|------|----------|
| PATCH | /users/{user_id}/ban | Бан/разбан пользователя | admin | AdminMessageResponse или UserPublic |
| GET | /stats | Статистика системы | admin | AdminStats |
| POST | /broadcast | Массовая рассылка | admin | BroadcastResult |

--------------------------------------------------
🧱 ОБЯЗАТЕЛЬНЫЕ ИМПОРТЫ
--------------------------------------------------
Файл обычно должен использовать:

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.admin import AdminBanAction, AdminStats, BroadcastCreate, BroadcastResult, AdminMessageResponse
from app.schemas.user import UserPublic
from app.services import admin_service
from app.api.dependencies.auth import get_current_user, get_admin_user

Если в проекте еще нет get_admin_user,
его обязательно нужно создать.
Именно dependency должна проверять, что текущий пользователь является админом,
например по tg_id в settings.ADMIN_IDS.
Проверку доступа обычно выносят в dependency/RBAC-слой,
а настройки приложения, включая значения из .env, удобно хранить в settings через Pydantic Settings. [web:322][web:323][web:326]

--------------------------------------------------
🚀 APIRouter ФАЙЛА
--------------------------------------------------
Роутер должен быть объявлен так:

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"]
)

Можно также сразу добавить типовые ошибки:
router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Admin access required"},
        404: {"description": "Not found"},
    }
)

Важно:
- prefix должен быть ровно "/api/v1/admin";
- не нужно писать "/admin" внутри каждого endpoint еще раз;
- все админские ручки должны быть в одном месте.

--------------------------------------------------
🔐 АВТОРИЗАЦИЯ И ПРОВЕРКА ADMIN
--------------------------------------------------
Ключевая идея:
api/admin.py не должен сам проверять admin-права в теле каждого endpoint.

Вместо этого должна существовать dependency:

async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.tg_id not in settings.ADMIN_IDS:
        raise HTTPException(status_code=403, detail="Admin access required")
    if current_user.is_banned:
        raise HTTPException(status_code=403, detail="User is banned")
    return current_user

Лучше, если проверка админа будет еще аккуратнее:
- current_user получаем через get_current_user;
- ADMIN_IDS читаются из settings;
- если юзер не админ — 403;
- если админ забанен — тоже 403.

Роуты admin.py должны использовать:
admin_user: User = Depends(get_admin_user)

Важно:
- не передавать tg_id администратора через query/body;
- не сравнивать вручную токен в каждом route;
- не хардкодить ADMIN_IDS в файле;
- не вызывать get_me() из другого роутера.

--------------------------------------------------
⚙️ НАСТРОЙКИ ADMIN_IDS
--------------------------------------------------
ADMIN_IDS должны приходить из .env через settings, а не хардкодиться.

Пример идеи:
ADMIN_IDS=[123456789, 987654321]

Важно:
- settings должны уметь читать список значений из окружения;
- формат списка должен быть согласован с parser-логикой проекта;
- роутер admin.py не должен сам парсить env.

Настройки приложения и переменные окружения обычно выносят в единый settings-класс, что упрощает поддержку и тестирование. [web:322][web:325]

--------------------------------------------------
✅ PATCH /users/{user_id}/ban
--------------------------------------------------
Назначение:
администратор банит или разбанивает пользователя.

Для этого лучше использовать входную схему:

class AdminBanAction(BaseModel):
    is_banned: bool

Правильная сигнатура:

@router.patch("/users/{user_id}/ban", response_model=AdminMessageResponse)
async def ban_user(
    user_id: int = Path(..., gt=0),
    payload: AdminBanAction,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    result = await admin_service.set_user_ban_status(
        db=db,
        user_id=user_id,
        is_banned=payload.is_banned,
        admin_user=admin_user,
    )
    return result

Альтернативный вариант:
возвращать response_model=UserPublic,
если после бана хочется отдать обновленный объект пользователя.

Но для MVP обычно достаточно:
{
  "message": "User banned"
}
или
{
  "message": "User unbanned"
}

Что должно делать admin_service.set_user_ban_status(...):
- найти пользователя;
- проверить, что он существует;
- запретить опасные кейсы, если нужно, например:
  - нельзя забанить самого себя;
  - нельзя забанить другого admin без дополнительного правила;
- обновить is_banned;
- сохранить изменения;
- вернуть результат.

Ошибки:
- 404 user not found
- 403 admin access required
- 400 invalid action
- 409 protected admin/self-ban forbidden (если такая логика предусмотрена)

--------------------------------------------------
✅ GET /stats
--------------------------------------------------
Назначение:
вернуть агрегированную статистику по системе.

Правильная сигнатура:

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    return await admin_service.get_stats(db=db)

Пример AdminStats:
class AdminStats(BaseModel):
    users: int
    themes: int
    requests: int
    banned_users: int | None = None
    pending_requests: int | None = None
    approved_requests: int | None = None

MVP минимум:
{
  "users": 100,
  "themes": 50,
  "requests": 200
}

Что делает admin_service.get_stats(...):
- считает количество пользователей;
- считает количество тем;
- считает количество заявок;
- при желании добавляет дополнительные агрегаты.

Важно:
- SQL агрегации не должны жить в роутере;
- роут просто вызывает service и возвращает схему.

--------------------------------------------------
✅ POST /broadcast
--------------------------------------------------
Назначение:
массовая рассылка сообщения пользователям от имени администратора.

Для этого лучше использовать входную схему:

class BroadcastCreate(BaseModel):
    text: str
    only_active: bool = True
    include_banned: bool = False

И выходную:

class BroadcastResult(BaseModel):
    total: int
    sent: int
    failed: int
    skipped: int

Правильная сигнатура:

@router.post("/broadcast", response_model=BroadcastResult)
async def broadcast_message(
    payload: BroadcastCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    return await admin_service.broadcast(
        db=db,
        text=payload.text,
        only_active=payload.only_active,
        include_banned=payload.include_banned,
        admin_user=admin_user,
    )

Что делает admin_service.broadcast(...):
- валидирует текст рассылки;
- выбирает целевую аудиторию;
- исключает banned пользователей, если include_banned=False;
- отправляет сообщения через bot service;
- считает sent/failed/skipped;
- возвращает агрегированный результат.

Важно:
- цикл отправки сообщений не должен быть в роутере;
- bot API не должен вызываться прямо из admin.py;
- фильтрация получателей должна жить в service.

Ошибки:
- 400 empty broadcast text
- 403 admin access required
- 500 bot sending failure (или частичный успех с failed > 0)

--------------------------------------------------
❌ ЧТО НЕПРАВИЛЬНО ДЕЛАТЬ В admin.py
--------------------------------------------------
Неправильные варианты:

1. Проверять admin права так:
   if current_user.tg_id not in [123, 456]:
       raise HTTPException(...)
   Это нельзя держать в каждом route.
   Должна быть единая dependency + settings.ADMIN_IDS. [web:322][web:323]

2. Делать так:
   async with AsyncSessionLocal() as session:
       ...
   Вместо этого должна быть зависимость:
   db: AsyncSession = Depends(get_db). [web:318][web:317]

3. Делать бан прямо в роутере:
   user = await db.get(User, user_id)
   user.is_banned = True
   await db.commit()
   Это business logic, ее место в service.

4. Делать select count(*) по users/themes/requests прямо в роутере.
   Статистика должна считаться в admin_service.

5. Делать массовую рассылку циклом прямо в endpoint.
   Это service/bot layer.

6. Возвращать сырые ORM-объекты без response_model.
   Лучше использовать типизированные схемы ответа. [web:327]

--------------------------------------------------
📤 RESPONSE MODELS
--------------------------------------------------
Роутер должен использовать response_model,
потому что это:
- документирует API;
- валидирует ответы;
- скрывает лишние поля;
- фиксирует контракт с фронтендом. [web:327]

Рекомендуемые схемы:

1. AdminBanAction
   Входная схема для PATCH /users/{user_id}/ban
   - is_banned: bool

2. AdminMessageResponse
   Простое сообщение для операций:
   - message: str

3. AdminStats
   Ответ GET /stats
   - users: int
   - themes: int
   - requests: int
   - banned_users: int | None
   - pending_requests: int | None
   - approved_requests: int | None

4. BroadcastCreate
   Входная схема для POST /broadcast
   - text: str
   - only_active: bool = True
   - include_banned: bool = False

5. BroadcastResult
   Ответ POST /broadcast
   - total: int
   - sent: int
   - failed: int
   - skipped: int

При желании PATCH /users/{user_id}/ban может возвращать UserPublic,
если фронту нужен обновленный объект пользователя.

--------------------------------------------------
⚠️ ОБРАБОТКА ОШИБОК
--------------------------------------------------
Роутер должен корректно переводить ошибки сервисов в HTTPException,
если в проекте пока нет глобального exception handler.

Типичные случаи:
- ForbiddenError → 403
- NotFoundError → 404
- BadRequestError → 400
- ConflictError → 409

FastAPI стандартно использует HTTPException для клиентских ошибок,
а ответы можно дополнительно описывать через responses в декораторах. [web:321][web:324]

Пример:
@router.patch(
    "/users/{user_id}/ban",
    response_model=AdminMessageResponse,
    responses={
        403: {"description": "Admin access required"},
        404: {"description": "User not found"},
    },
)

--------------------------------------------------
🧪 ЧТО ДОЛЖНО БЫТЬ ПРОТЕСТИРОВАНО
--------------------------------------------------
Минимальные тесты для api/admin.py:

1. PATCH /users/{user_id}/ban success
   - admin банит пользователя
   - 200 OK

2. PATCH /users/{user_id}/ban unban success
   - admin разбанивает пользователя
   - 200 OK

3. PATCH /users/{user_id}/ban forbidden
   - не admin
   - 403

4. PATCH /users/{user_id}/ban not found
   - user не существует
   - 404

5. GET /stats success
   - admin получает статистику
   - ответ содержит users/themes/requests

6. GET /stats forbidden
   - не admin
   - 403

7. POST /broadcast success
   - admin отправляет рассылку
   - ответ содержит total/sent/failed/skipped

8. POST /broadcast empty text
   - 400 или 422

9. POST /broadcast forbidden
   - не admin
   - 403

10. Проверка ADMIN_IDS
   - tg_id из settings.ADMIN_IDS проходит
   - любой другой tg_id не проходит

--------------------------------------------------
📁 РЕКОМЕНДУЕМАЯ ФИНАЛЬНАЯ СТРУКТУРА ФАЙЛА
--------------------------------------------------
1. imports
2. router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
3. PATCH /users/{user_id}/ban
4. GET /stats
5. POST /broadcast

Важно:
внутри файла не должно быть:
- ручного парсинга .env;
- ручного SQL;
- логики бана/рассылки/статистики;
- хардкода ADMIN_IDS;
- вызовов бота напрямую.

--------------------------------------------------
💡 MVP vs PRODUCTION
--------------------------------------------------
MVP минимум:
- router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
- Depends(get_admin_user) на всех ручках
- PATCH /users/{user_id}/ban
- GET /stats
- POST /broadcast
- response_model
- корректные 403/404/400

Production:
+ логирование админских действий
+ защита от self-ban
+ аудит broadcast операций
+ фоновая отправка рассылки
+ расширенная статистика
+ rate limiting для broadcast
+ global exception handlers

--------------------------------------------------
✅ ИТОГ
--------------------------------------------------
api/admin.py считается сделанным правильно только если:

1. Он использует APIRouter(prefix="/api/v1/admin", tags=["admin"]).
2. Все ручки доступны только через Depends(get_admin_user).
3. ADMIN_IDS берутся из settings, а не хардкодятся в роутере.
4. PATCH /users/{user_id}/ban не содержит бизнес-логики бана внутри route.
5. GET /stats не делает SQL прямо в роутере.
6. POST /broadcast не отправляет сообщения прямо из route.
7. Все ответы типизированы через response_model.
8. Ошибки сервиса превращаются в корректные HTTP статусы.

Главная мысль:
api/admin.py должен быть тонким админским роутером,
а не местом, где вручную пишутся auth, SQL, баны и бот-рассылка.
"""
