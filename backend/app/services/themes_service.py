"""
✅ BACKEND B: THEMES SERVICE (ПОЛНОЕ ОПИСАНИЕ)
==================================================
Бизнес-логика тем встреч: создание, получение списка, просмотр детали,
удаление и все проверки, связанные с темами.

🎯 ЦЕЛЬ ФАЙЛА:
Слой services не должен знать о FastAPI роутерах и HTTP-эндпоинтах как о URL,
но именно здесь должна находиться основная бизнес-логика работы с темами:
- кто может создавать тему;
- какие данные считаются валидными;
- какие темы можно показывать в списке;
- как получить одну тему;
- кто может удалить тему;
- какие ошибки выбрасывать в бизнес-кейсах.

API-слой (app/api/themes.py) должен быть тонким:
роут принимает запрос → вызывает функцию из themes_service → возвращает ответ.

--------------------------------------------------
📦 ЗОНА ОТВЕТСТВЕННОСТИ THEMES SERVICE
--------------------------------------------------
Themes service отвечает за:

1. Создание темы встречи.
2. Получение списка тем с фильтрацией и пагинацией.
3. Получение одной темы по id.
4. Подсчет/подготовку дополнительных данных для темы:
   - количество заявок;
   - количество свободных мест;
   - признак доступности записи.
5. Удаление темы с проверкой прав.
6. Бизнес-валидацию:
   - пользователь не забанен;
   - дата в будущем;
   - limit/offset валидны;
   - тема существует;
   - пользователь имеет право на удаление.

Themes service НЕ должен:
- парсить HTTP Request напрямую;
- работать с APIRouter;
- возвращать JSONResponse;
- описывать response_model;
- заниматься Swagger/OpenAPI;
- делать преобразование ORM → Pydantic (это задача API/schemas слоя).

--------------------------------------------------
📋 ОСНОВНЫЕ ФУНКЦИИ ФАЙЛА
--------------------------------------------------
| Функция | Назначение | Кто вызывает |
|---------|------------|--------------|
| create_theme | Создать новую тему | api/themes.py POST /themes |
| get_themes | Вернуть список тем | api/themes.py GET /themes |
| get_theme_by_id | Вернуть одну тему | api/themes.py GET /themes/{id} |
| delete_theme | Удалить тему | api/themes.py DELETE /themes/{id} |
| count_theme_requests | Подсчет числа заявок | внутреннее использование |
| get_theme_slots_info | Подсчет занятых/свободных слотов | внутреннее использование |
| can_manage_theme | Проверка прав creator/admin | внутреннее использование |

--------------------------------------------------
🧱 ПРЕДПОЛАГАЕМЫЕ ЗАВИСИМОСТИ
--------------------------------------------------
Файл обычно использует:

from datetime import datetime, timezone
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.theme import Theme
from app.models.user import User
from app.models.request import Request
from app.schemas.theme import ThemeCreate
# при наличии enum:
# from app.models.request import RequestStatus

Дополнительно допустимы:
- кастомные исключения проекта;
- стандартный HTTPException (если пока нет своего слоя exceptions).

Рекомендуемый подход:
лучше поднимать бизнес-ошибки через свои исключения,
а в API-слое уже маппить их в HTTP-коды. Надежная обработка ошибок и явный контракт
между service и route считаются хорошей практикой для FastAPI-приложений. [web:288][web:294]

--------------------------------------------------
🧠 БИЗНЕС-ПРАВИЛА
--------------------------------------------------
1. Создавать темы может только авторизованный пользователь.
2. Забаненный пользователь не может создавать темы.
3. Дата и время темы должны быть строго в будущем.
4. Заголовок темы не должен быть пустым.
5. Лимит выборки должен быть положительным.
6. Offset не может быть отрицательным.
7. Удалять тему может только:
   - создатель темы;
   - администратор.
8. Если тема не существует — вернуть ошибку not found.
9. При получении списка тем по умолчанию желательно возвращать
   только актуальные темы (например, future_only=True).
10. Список должен быть отсортирован предсказуемо, например:
   по datetime ASC (ближайшие встречи сначала). Фильтрация и пагинация
   должны быть явными и стабильными для клиентов API. [web:285][web:290][web:293]

--------------------------------------------------
🧩 ПРЕДПОЛАГАЕМАЯ СИГНАТУРА ФУНКЦИЙ
--------------------------------------------------

1. CREATE

async def create_theme(
    db: AsyncSession,
    creator: User,
    theme_ ThemeCreate,
) -> Theme:
    '''
    Создает новую тему встречи и сохраняет ее в БД.
    Возвращает ORM объект Theme после commit + refresh.
    '''

2. LIST

async def get_themes(
    db: AsyncSession,
    *,
    limit: int = 10,
    offset: int = 0,
    future_only: bool = True,
) -> list[Theme]:
    '''
    Возвращает список тем с пагинацией и опциональной фильтрацией
    только будущих встреч.
    '''

3. DETAIL

async def get_theme_by_id(
    db: AsyncSession,
    theme_id: int,
) -> Theme:
    '''
    Возвращает одну тему по id.
    Если тема не найдена — выбрасывает исключение.
    '''

4. DELETE

async def delete_theme(
    db: AsyncSession,
    theme_id: int,
    current_user: User,
    *,
    is_admin: bool = False,
) -> None:
    '''
    Удаляет тему, если текущий пользователь — автор темы или администратор.
    '''

5. SUPPORT: count requests

async def count_theme_requests(
    db: AsyncSession,
    theme_id: int,
) -> int:
    '''
    Возвращает количество заявок по теме.
    '''

6. SUPPORT: slots info

async def get_theme_slots_info(
    db: AsyncSession,
    theme_id: int,
    max_slots: int = 30,
) -> dict:
    '''
    Возвращает словарь:
    {
        "requests_count": int,
        "slots_taken": int,
        "slots_available": int,
        "is_full": bool
    }
    '''

7. SUPPORT: permissions

def can_manage_theme(
    theme: Theme,
    user: User,
    *,
    is_admin: bool = False,
) -> bool:
    '''
    Проверяет, может ли пользователь управлять темой.
    '''
    
--------------------------------------------------
✅ ПОЛНОЕ ПОВЕДЕНИЕ create_theme()
--------------------------------------------------
Функция create_theme обязана:

1. Проверить, что creator передан и существует.
2. Проверить, что creator.is_banned == False.
3. Проверить, что theme_data.title не пустой.
4. Проверить, что theme_data.datetime > now().
5. При необходимости проверить длину title/description
   (если это не полностью покрыто Pydantic-схемой).
6. Создать объект Theme:
   Theme(
       title=theme_data.title,
       description=theme_data.description,
       datetime=theme_data.datetime,
       location=theme_data.location,
       max_slots=theme_data.max_slots,
       creator_id=creator.id,
   )
7. Добавить объект в сессию.
8. Выполнить await db.commit().
9. Выполнить await db.refresh(theme).
10. Вернуть готовый ORM объект.

Почему нужен refresh:
после commit объект должен содержать актуальные поля из БД,
например id и created_at; для async SQLAlchemy это типичный паттерн
после вставки новой сущности. [web:286][web:289][web:292]

--------------------------------------------------
❌ ОШИБКИ create_theme()
--------------------------------------------------
create_theme должна выбрасывать ошибку, если:

- creator is None
- creator.is_banned == True
- дата в прошлом или равна текущему моменту
- title пустой или состоит только из пробелов
- location невалидна (если есть дополнительная бизнес-валидация)
- max_slots < 1 (если это не гарантируется схемой)

Рекомендуемые статусы на уровне API:
- 403 Forbidden — забаненный пользователь;
- 400 Bad Request — невалидная дата/бизнес-ошибка;
- 422 Unprocessable Entity — ошибки схемы/Pydantic до входа в service. [web:285][web:294]

--------------------------------------------------
✅ ПОЛНОЕ ПОВЕДЕНИЕ get_themes()
--------------------------------------------------
Функция get_themes обязана:

1. Принять limit, offset, future_only.
2. Проверить:
   - limit > 0
   - offset >= 0
   - limit не слишком велик (например, не более 100)
3. Построить select(Theme).
4. Если future_only=True:
   добавить фильтр Theme.datetime > now().
5. Добавить сортировку:
   ORDER BY Theme.datetime ASC
6. Добавить пагинацию:
   LIMIT limit OFFSET offset
7. При необходимости заранее подгрузить creator:
   selectinload(Theme.creator)
8. Вернуть список ORM объектов.

Рекомендуемая сортировка:
сначала ближайшие предстоящие встречи. Для API списка важны
стабильная сортировка и явная пагинация. [web:290][web:293]

--------------------------------------------------
📌 ДОПОЛНИТЕЛЬНО ДЛЯ get_themes()
--------------------------------------------------
Если фронтенду нужен более богатый ответ, service может дополнительно
уметь возвращать total_count или has_more, но это нужно зафиксировать заранее.

Вариант 1 — простой:
get_themes(...) -> list[Theme]

Вариант 2 — расширенный:
get_themes(...) -> tuple[list[Theme], int]

где int = total_count

Или:
{
    "items": [...],
    "total": int,
    "limit": int,
    "offset": int,
    "has_more": bool
}

Если вы хотите “максимально полное” решение, лучше сразу договориться
о расширенном контракте, потому что фронтенду почти всегда нужны total_count
и has_more для пагинации. [web:290][web:293]

Рекомендуемый вариант для вашего проекта:
async def get_themes(...) -> tuple[list[Theme], int]

--------------------------------------------------
✅ ПОЛНОЕ ПОВЕДЕНИЕ get_theme_by_id()
--------------------------------------------------
Функция обязана:

1. Получить theme_id.
2. Проверить, что theme_id > 0.
3. Выполнить запрос к БД:
   - по id;
   - желательно с selectinload(Theme.creator)
4. Если тема не найдена — выбросить исключение not found.
5. Вернуть ORM объект Theme.

Если нужно отображать число заявок/слотов,
то API-слой после вызова get_theme_by_id() может отдельно вызвать
get_theme_slots_info(), либо service может иметь специальную функцию
get_theme_detail() с уже подготовленными связанными данными. [web:275][web:282][web:288]

--------------------------------------------------
✅ ПОЛНОЕ ПОВЕДЕНИЕ delete_theme()
--------------------------------------------------
Функция delete_theme обязана:

1. Получить тему через get_theme_by_id().
2. Проверить права:
   - current_user.id == theme.creator_id
   - ИЛИ is_admin == True
3. Если прав нет — выбросить forbidden.
4. Выполнить удаление.
5. Зафиксировать транзакцию через commit().
6. Ничего не возвращать, либо вернуть удаленную тему
   (если это нужно API).

Рекомендация для MVP:
- hard delete допустим;
- но надо явно зафиксировать, что это физическое удаление записи.

Альтернатива:
soft delete через поле is_deleted / deleted_at,
если хотите сохранять историю. Но если такого поля в модели нет,
значит для MVP у вас именно hard delete. [web:275][web:287][web:288]

--------------------------------------------------
✅ SUPPORT: count_theme_requests()
--------------------------------------------------
Назначение:
подсчитать, сколько заявок привязано к теме.

Базовый вариант:
SELECT COUNT(*) FROM requests WHERE theme_id = :theme_id

Если у вас есть статусы заявок, нужно заранее зафиксировать:
считать все заявки или только approved/pending.

Рекомендуемый вариант для вашего проекта:
- requests_count = общее количество заявок;
- slots_taken = количество approved заявок;
- это лучше различать отдельно.

--------------------------------------------------
✅ SUPPORT: get_theme_slots_info()
--------------------------------------------------
Назначение:
дать фронту и API понятную информацию о загруженности темы.

Ожидаемая логика:
1. Посчитать общее число заявок.
2. Посчитать число approved заявок.
3. Определить max_slots:
   - из Theme.max_slots, если поле есть;
   - иначе использовать дефолт 30.
4. Вычислить:
   slots_taken = approved_count
   slots_available = max_slots - slots_taken
   is_full = slots_available <= 0

Возвращаемый результат:
{
    "requests_count": 12,
    "approved_count": 7,
    "slots_taken": 7,
    "slots_available": 23,
    "is_full": False,
}

Такие вычисления полезно держать в service-слое, а не в роутере,
потому что это уже бизнес-логика домена. [web:275][web:278][web:284]

--------------------------------------------------
✅ SUPPORT: can_manage_theme()
--------------------------------------------------
Функция возвращает True, если:
- user.id == theme.creator_id
- или is_admin == True

Во всех остальных случаях — False.

Это небольшая, но полезная функция:
она убирает дублирование логики из delete_theme и будущего update_theme.

--------------------------------------------------
🔄 ТРАНЗАКЦИИ И РАБОТА С БД
--------------------------------------------------
Для операций изменения состояния требуется аккуратная работа с транзакцией:

- create_theme:
  db.add(theme)
  await db.commit()
  await db.refresh(theme)

- delete_theme:
  await db.delete(theme)
  await db.commit()

При ошибке коммита должен выполняться rollback.
Если в проекте централизованно rollback делает внешний слой — это нужно
зафиксировать. Если нет, service должен сам делать try/except и rollback.

Rollback в SQLAlchemy влияет на состояние объектов сессии,
поэтому это поведение надо учитывать при обработке ошибок. [web:289][web:292]

Рекомендуемый шаблон:
try:
    ...
    await db.commit()
except Exception:
    await db.rollback()
    raise

--------------------------------------------------
🧪 ПОЛНЫЙ СПИСОК ТЕСТОВ
--------------------------------------------------
Минимум для tests/unit/test_themes.py:

1. test_create_theme_success
   - валидный creator
   - дата в будущем
   - тема создается

2. test_create_theme_banned_user
   - creator.is_banned = True
   - ожидаем forbidden

3. test_create_theme_past_datetime
   - дата в прошлом
   - ожидаем bad request

4. test_create_theme_empty_title
   - title=""
   - ожидаем validation/business error

5. test_get_themes_default
   - возвращается список тем
   - сортировка корректная

6. test_get_themes_future_only
   - прошедшие темы не входят в выборку

7. test_get_themes_with_offset_limit
   - limit/offset работают корректно

8. test_get_themes_invalid_limit
   - limit=0 или <0
   - ожидаем ошибку

9. test_get_theme_by_id_success
   - тема находится по id

10. test_get_theme_by_id_not_found
   - несуществующий id
   - ожидаем not found

11. test_delete_theme_by_creator
   - автор может удалить тему

12. test_delete_theme_by_admin
   - админ может удалить тему

13. test_delete_theme_forbidden
   - не автор и не админ
   - ожидаем forbidden

14. test_count_theme_requests
   - корректно считает число заявок

15. test_get_theme_slots_info
   - корректно считает approved_count и slots_available

--------------------------------------------------
🧾 ПРИМЕРЫ КОНТРАКТА ФУНКЦИЙ
--------------------------------------------------

async def create_theme(db, creator, theme_data) -> Theme
- вход: AsyncSession, User, ThemeCreate
- выход: Theme
- ошибки: Forbidden / BadRequest / IntegrityError wrapper

async def get_themes(db, limit=10, offset=0, future_only=True) -> tuple[list[Theme], int]
- вход: AsyncSession + параметры списка
- выход: (themes, total_count)
- ошибки: BadRequest при невалидных параметрах

async def get_theme_by_id(db, theme_id) -> Theme
- вход: AsyncSession, int
- выход: Theme
- ошибки: NotFound

async def delete_theme(db, theme_id, current_user, is_admin=False) -> None
- вход: AsyncSession, id темы, текущий пользователь
- выход: None
- ошибки: NotFound / Forbidden

--------------------------------------------------
🚀 РЕКОМЕНДУЕМАЯ ФИНАЛЬНАЯ СТРУКТУРА ФАЙЛА
--------------------------------------------------

1. imports
2. private helper functions:
   - _validate_theme_datetime(...)
   - _validate_pagination(...)
3. public service functions:
   - create_theme(...)
   - get_themes(...)
   - get_theme_by_id(...)
   - delete_theme(...)
4. support functions:
   - count_theme_requests(...)
   - get_theme_slots_info(...)
   - can_manage_theme(...)

--------------------------------------------------
💡 РЕКОМЕНДАЦИИ ДЛЯ ВАШЕГО ПРОЕКТА
--------------------------------------------------
MVP-минимум для первого рабочего варианта:
- create_theme
- get_themes
- get_theme_by_id
- delete_theme

Хороший production-like вариант:
- create_theme
- get_themes (с total_count)
- get_theme_by_id
- delete_theme
- count_theme_requests
- get_theme_slots_info
- can_manage_theme
- update_theme (позже)

--------------------------------------------------
✅ ИТОГ
--------------------------------------------------
Этот файл должен быть единой точкой бизнес-логики тем встреч.
Если в api/themes.py появляется проверка banned, прав доступа,
или логика подсчета слотов — значит часть бизнес-логики утекла из service слоя,
и структуру нужно поправить.

ЦЕЛЬ:
routes тонкие,
services умные,
schemas валидируют,
models хранят данные,
tests проверяют бизнес-правила.
"""


from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from datetime import datetime, timezone
from ..models.theme import Theme
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from ..core.db import AsyncSessionLocal
from ..schemas.theme import ThemeCreate
from ..models.user import User

async def create_theme(db: AsyncSession, creator: User, theme_: ThemeCreate) -> Theme:
    if creator.is_banned:
        raise HTTPException(status_code = 403, detail = "Пользователь заблокирован")

    if theme_.datetime < datetime.now(timezone.utc):
        raise HTTPException(status_code = 400, detail = "Некорректная дата встречи")

    theme = Theme(title = theme_.title, description = theme_.description, datetime = theme_.datetime, location = theme_.location,
                 creator_id = creator.id, max_slots = theme_.max_slots)

    db.add(theme)
    await db.commit()

    return theme

async def get_themes(db: AsyncSession) -> list:
    limit = 10

    query = select(Theme)
    query = query.where(Theme.datetime > datetime.now())

    query = query.order_by(Theme.datetime).limit(limit)

    result = await db.execute(query)
    themes = result.scalars().all()

    return themes

async def get_theme(db: AsyncSession, theme_id: int) -> Theme:
    query = select(Theme).where(Theme.id == theme_id)
    result = await db.execute(query)
    exactTheme = result.scalar_one_or_none()

    if exactTheme is None:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    return exactTheme


async def delete_theme(db: AsyncSession, theme_id: int, current_user: User):
    query = select(Theme).where(Theme.id == theme_id)
    result = await db.execute(query)
    exactTheme = result.scalar_one_or_none()

    if exactTheme is None:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    if exactTheme.creator_id != current_user.id: # and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет прав на удаление этой темы")

    await db.delete(exactTheme)
    await db.commit()

    return "Успешное удаление"
