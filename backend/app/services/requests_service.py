"""
⏳ BACKEND C: REQUESTS SERVICE
==================================================
Логика заявок + уведомлений

📋 ФУНКЦИИ (Backend C):
| Функция | Описание |
|---------|----------|
| create_request | Подать заявку (!duplicate) |
| moderate_request | Approve/Reject + notify |
| get_requests_for_theme | Список для модератора |

⏳ TODO Неделя 2:
async def create_request(db, theme_id: int, user: User) -> Request:
    if await exists(db, theme_id, user.id): raise HTTPConflict
    if theme.requests_count >= 30: raise HTTPBadRequest
    request = Request(theme_id=theme_id, user_id=user.id, status="pending")
    # notify bot? await moderate_request(request.id, "auto_pending")

async def moderate_request(db, request_id: int, status: str):
    request = await db.get(Request, request_id)
    request.status = status
    if status == "approved":
        await bots.notify_user(request.user.tg_id, "Вас приняли!")
"""
