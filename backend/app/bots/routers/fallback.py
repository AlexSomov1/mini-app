from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
async def cmd_help(message: Message):
    from ..texts.start import HELP
    await message.answer(HELP)

@router.message()
async def fallback(message: Message):
    await message.answer("🤔 Я не понял команду. Используйте /start или /help")