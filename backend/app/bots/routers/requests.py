import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from app.core.db import AsyncSessionLocal
from app.services import users_service, requests_service, themes_service
from app.schemas.request import RequestStatus
from ..utils.callback_data import RequestAction
from ..services.notification import notify_user_about_decision

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(RequestAction.filter())
async def process_moderation(callback: CallbackQuery, callback_data: RequestAction):
    request_id = callback_data.request_id
    new_status = RequestStatus.approved if callback_data.action == "approve" else RequestStatus.rejected
    moderator_tg_id = callback.from_user.id

    try:
        async with AsyncSessionLocal() as db:
            # 1. Находим модератора в БД
            moderator = await users_service.get_user_by_tg_id(db, moderator_tg_id)
            if not moderator or not (moderator.is_admin or True): # В проде добавить проверку creator темы
                await callback.answer("Нет прав для модерации", show_alert=True)
                return

            # 2. Вызываем сервис модерации
            updated_request = await requests_service.moderate_request(db, request_id, new_status, moderator)
            
            # 3. Уведомляем пользователя
            if updated_request.user and updated_request.theme:
                await notify_user_about_decision(
                    bot=callback.bot,
                    user_chat_id=updated_request.user.tg_id,
                    theme_title=updated_request.theme.title,
                    status=new_status.value
                )

            await callback.message.edit_text(f"✅ Заявка обработана: <b>{new_status.value}</b>.")
            await callback.answer("Готово!")

    except Exception as e:
        logger.error(f"Moderation error: {e}")
        try:
            await callback.answer("Ошибка при обработке заявки", show_alert=True)
        except TelegramBadRequest:
            pass