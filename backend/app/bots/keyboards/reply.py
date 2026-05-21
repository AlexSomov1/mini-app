from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from ..config import config

def get_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="📱 Открыть приложение", web_app=WebAppInfo(url=config.WEBAPP_URL))
        ], [
            KeyboardButton(text="📚 Мои темы"),
            KeyboardButton(text="📝 Мои заявки")
        ]],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )