"""
🔒 SECURITY — авторизация и валидация
==================================================
Backend D (Неделя 3): Telegram initData + JWT

📋 ФУНКЦИИ:
| Функция | Описание |
|---------|----------|
| verify_init_data | Проверить подпись Telegram |
| get_current_user | initData → User |
| is_admin | user.tg_id in settings.admin_ids |

⏳ TODO Неделя 3:
def verify_init_data(init_ str) -> dict:
    # Алгоритм проверки hash из Telegram docs
    data_check_string = "\n".join([k + "=" + v for k, v in sorted(data.items())])
    secret_key = hmac.new("WebAppData", data_check_string.encode(), "SHA256")
	# ...
"""

import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import parse_qsl


class TelegramInitDataError(ValueError):
    """Raised when Telegram WebApp initData is missing or invalid."""


def verify_telegram_init_data(
    init_data: str,
    bot_token: str,
    max_age_seconds: int | None = 60 * 60 * 24,
) -> dict[str, Any]:
    if not init_data:
        raise TelegramInitDataError("Telegram initData is empty")

    if not bot_token:
        raise TelegramInitDataError("BOT_TOKEN is not configured")

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise TelegramInitDataError("Telegram initData hash is missing")

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(parsed.items())
    )
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode(),
        hashlib.sha256,
    ).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise TelegramInitDataError("Telegram initData hash is invalid")

    if max_age_seconds is not None:
        try:
            auth_date = int(parsed["auth_date"])
        except (KeyError, ValueError) as exc:
            raise TelegramInitDataError("Telegram initData auth_date is invalid") from exc

        now = int(time.time())
        if now - auth_date > max_age_seconds:
            raise TelegramInitDataError("Telegram initData is expired")
        if auth_date - now > 300:
            raise TelegramInitDataError("Telegram initData auth_date is in the future")

    user_raw = parsed.get("user")
    if user_raw:
        try:
            parsed["user"] = json.loads(user_raw)
        except json.JSONDecodeError as exc:
            raise TelegramInitDataError("Telegram initData user payload is invalid") from exc

    return parsed
