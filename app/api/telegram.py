from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
import redis.asyncio as redis

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas.api_token import TelegramLinkResponse

router = APIRouter(prefix="/auth/telegram", tags=["telegram"])


@router.post("/link", response_model=TelegramLinkResponse)
async def link_telegram(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Привязка Telegram аккаунта к текущему пользователю.
    Генерирует уникальный код для подтверждения в боте.
    """
    link_code = secrets.token_urlsafe(16)
    
    redis_client = await redis.from_url(settings.REDIS_URL)
    await redis_client.setex(f"telegram_link:{link_code}", 600, current_user.email)
    
    return TelegramLinkResponse(
        message=f"Для привязки Telegram аккаунта используйте команду в боте:\n/link {link_code}\n\nКод действителен 10 минут.",
        telegram_chat_id=0
    )


@router.post("/link/confirm")
async def confirm_telegram_link(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Подтверждение привязки Telegram аккаунта после подтверждения в боте.
    """
    redis_client = await redis.from_url(settings.REDIS_URL)
    
    telegram_chat_id = await redis_client.get(f"telegram_linked:{current_user.email}")
    
    if telegram_chat_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram link not confirmed"
        )
    
    telegram_chat_id = int(telegram_chat_id.decode('utf-8'))
    
    result = await db.execute(
        select(User).where(User.telegram_chat_id == telegram_chat_id)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user is not None and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This Telegram account is already linked to another user"
        )
    
    current_user.telegram_chat_id = telegram_chat_id
    current_user.telegram_linked_at = datetime.now(timezone.utc)
    
    await redis_client.delete(f"telegram_linked:{current_user.email}")
    
    await db.commit()
    
    return TelegramLinkResponse(
        message="Telegram account linked successfully",
        telegram_chat_id=telegram_chat_id
    )


@router.post("/unlink")
async def unlink_telegram(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Отвязка Telegram аккаунта от текущего пользователя.
    """
    current_user.telegram_chat_id = None
    current_user.telegram_linked_at = None
    
    await db.commit()
    
    return {"message": "Telegram account unlinked successfully"}

