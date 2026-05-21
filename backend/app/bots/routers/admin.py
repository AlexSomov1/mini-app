import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from app.core.db import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select
from ..states.broadcast import BroadcastState
from ..texts.admin import BROADCAST_PROMPT, BROADCAST_CONFIRM, BROADCAST_DONE, ADMIN_ONLY
from ..config import config

router = Router()
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS

@router.message(Command("broadcast"))
async def start_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer(ADMIN_ONLY)
    await state.set_state(BroadcastState.waiting_text)
    await message.answer(BROADCAST_PROMPT)

@router.message(BroadcastState.waiting_text)
async def receive_broadcast_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(BroadcastState.waiting_confirm)
    await message.answer("📤 Текст сохранен. Введите /send для отправки или /cancel для отмены.")

@router.message(Command("send"), BroadcastState.waiting_confirm)
async def send_broadcast(message: Message, state: FSMContext, bot):
    if not is_admin(message.from_user.id): return
    data = await state.get_data()
    text = data.get("text", "")
    
    sent = 0
    failed = 0
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.is_banned == False))
        users = result.scalars().all()
        
        for user in users:
            try:
                await bot.send_message(chat_id=user.tg_id, text=text)
                sent += 1
            except Exception:
                failed += 1
                
    await message.answer(BROADCAST_DONE.format(sent=sent, failed=failed))
    await state.clear()

@router.message(Command("cancel"), BroadcastState.waiting_confirm)
async def cancel_broadcast(message: Message, state: FSMContext):
    await message.answer("❌ Рассылка отменена.")
    await state.clear()