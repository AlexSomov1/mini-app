from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.security import TelegramInitDataError, verify_telegram_init_data
from app.models.user import User
from app.services import users_service


def _extract_init_data(
    authorization: str | None,
    x_telegram_init_data: str | None,
) -> str | None:
    if x_telegram_init_data:
        return x_telegram_init_data

    if not authorization:
        return None

    scheme, separator, credentials = authorization.partition(" ")
    if separator and scheme.lower() in {"tma", "bearer"}:
        return credentials.strip()

    if "auth_date=" in authorization and "hash=" in authorization:
        return authorization.strip()

    return None


def _full_name_from_telegram_user(telegram_user: dict) -> str:
    full_name = " ".join(
        part
        for part in (
            telegram_user.get("first_name"),
            telegram_user.get("last_name"),
        )
        if part
    ).strip()
    return full_name or telegram_user.get("username") or str(telegram_user["id"])


async def get_optional_user(
    authorization: Annotated[str | None, Header()] = None,
    x_telegram_init_data: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User | None:
    init_data = _extract_init_data(authorization, x_telegram_init_data)
    if not init_data:
        return None

    return await _user_from_init_data(init_data=init_data, db=db)


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    x_telegram_init_data: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    init_data = _extract_init_data(authorization, x_telegram_init_data)
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram initData is required",
        )

    user = await _user_from_init_data(init_data=init_data, db=db)
    if user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is banned")

    return user


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin and current_user.tg_id not in settings.admin_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


async def _user_from_init_data(init_data: str, db: AsyncSession) -> User:
    try:
        telegram_data = verify_telegram_init_data(init_data, settings.bot_token)
    except TelegramInitDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    telegram_user = telegram_data.get("user")
    if not isinstance(telegram_user, dict) or "id" not in telegram_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram user payload is required",
        )

    tg_id = int(telegram_user["id"])
    user = await users_service.get_or_create_user(
        db=db,
        tg_id=tg_id,
        username=telegram_user.get("username"),
        full_name=_full_name_from_telegram_user(telegram_user),
    )

    if tg_id in settings.admin_ids and not user.is_admin:
        user.is_admin = True
        await db.commit()
        await db.refresh(user)

    return user
