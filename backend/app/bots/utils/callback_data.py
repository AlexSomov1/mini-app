from aiogram.filters.callback_data import CallbackData

class RequestAction(CallbackData, prefix="req"):
    action: str  # "approve" | "reject"
    request_id: int

class AdminAction(CallbackData, prefix="admin"):
    action: str  # "broadcast_confirm" | "broadcast_cancel"