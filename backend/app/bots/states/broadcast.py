from aiogram.fsm.state import State, StatesGroup

class BroadcastState(StatesGroup):
    waiting_text = State()
    waiting_confirm = State()