from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..utils.callback_data import RequestAction

def get_moderation_kb(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=RequestAction(action="approve", request_id=request_id).pack()),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=RequestAction(action="reject", request_id=request_id).pack())
        ]
    ])