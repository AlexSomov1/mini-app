"""
⏳ BACKEND B: THEMES SERVICE
==================================================
Бизнес-логика тем встреч

📋 ФУНКЦИИ (Backend B):
| Функция | Описание |
|---------|----------|
| create_theme | Создать тему (validate creator !banned) |
| get_themes | Список (?future_only, limit=10) |
| get_theme | Детали темы + кол-во слотов |
| delete_theme | Только creator или admin |

⏳ TODO Неделя 2:
async def create_theme(db, creator: User, theme_ ThemeCreate) -> Theme:
    if creator.is_banned: raise HTTPForbidden
    if theme_data.datetime < datetime.now(): raise HTTPBadRequest
    theme = Theme(**theme_data.dict(), creator_id=creator.id)
    db.add(theme); await db.commit()
    return theme

🧪 ТЕСТЫ:
async def test_create_theme_banned_user():
    creator.is_banned = True
    with pytest.raises(HTTPForbidden): await create_theme(...)
"""
