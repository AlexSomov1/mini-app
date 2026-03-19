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
