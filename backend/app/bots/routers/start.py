from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from ..keyboards.reply import get_main_kb
from ..texts.start import WELCOME

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    name = message.from_user.full_name or "друг"
    await message.answer(WELCOME.format(name=name), reply_markup=get_main_kb())