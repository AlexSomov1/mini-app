import logging
from aiogram import Bot
from ..keyboards.inline import get_moderation_kb
from ..texts.requests import NEW_REQUEST, REQUEST_APPROVED, REQUEST_REJECTED

logger = logging.getLogger(__name__)

async def notify_creator_about_request(bot: Bot, creator_chat_id: int, theme_title: str, applicant_name: str, request_id: int):
    try:
        await bot.send_message(
            chat_id=creator_chat_id,
            text=NEW_REQUEST.format(theme_title=theme_title, user_name=applicant_name),
            reply_markup=get_moderation_kb(request_id=request_id)
        )
    except Exception as e:
        logger.error(f"Failed to notify creator {creator_chat_id}: {e}")

async def notify_user_about_decision(bot: Bot, user_chat_id: int, theme_title: str, status: str):
    text = REQUEST_APPROVED.format(theme_title=theme_title) if status == "approved" else REQUEST_REJECTED.format(theme_title=theme_title)
    try:
        await bot.send_message(chat_id=user_chat_id, text=text)
    except Exception as e:
        logger.error(f"Failed to notify user {user_chat_id}: {e}")