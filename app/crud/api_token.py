from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
import hashlib

from app.models.api_token import APIToken


def generate_token() -> tuple[str, str]:
    """
    Генерация нового токена.
    
    Returns:
        Tuple (plain_token, token_hash)
    """
    plain_token = f"mgc_{secrets.token_urlsafe(32)}"
    token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
    token_prefix = plain_token[:8]
    
    return plain_token, token_hash, token_prefix


async def create_token(
    db: AsyncSession,
    name: str,
    user_id: Optional[UUID] = None,
    permission_mode: str = "inherit",
    custom_permissions: Optional[str] = None,
    rate_limit_per_minute: int = 30,
    rate_limit_per_hour: int = 500,
    expires_at: Optional[datetime] = None,
    issued_for: str = "user",
    allowed_ips: Optional[str] = None,
    description: Optional[str] = None
) -> tuple[APIToken, str]:
    """
    Создание нового API токена.
    
    Returns:
        Tuple (APIToken, plain_token)
    """
    plain_token, token_hash, token_prefix = generate_token()
    
    token = APIToken(
        name=name,
        token_prefix=token_prefix,
        token_hash=token_hash,
        user_id=user_id,
        custom_permissions=custom_permissions,
        rate_limit_per_minute=rate_limit_per_minute,
        rate_limit_per_hour=rate_limit_per_hour,
        expires_at=expires_at,
        issued_for=issued_for,
        permission_mode=permission_mode,
        allowed_ips=allowed_ips,
        description=description
    )
    
    db.add(token)
    await db.commit()
    await db.refresh(token)
    
    return token, plain_token


async def rotate_token(
    db: AsyncSession,
    token_id: UUID
) -> tuple[APIToken, str]:
    """
    Ротация токена.
    
    Returns:
        Tuple (APIToken, plain_token)
    """
    result = await db.execute(
        select(APIToken).where(APIToken.id == token_id)
    )
    token = result.scalar_one_or_none()
    
    if token is None:
        raise ValueError("Token not found")
    
    plain_token, token_hash, token_prefix = generate_token()
    
    token.token_hash = token_hash
    token.token_prefix = token_prefix
    
    await db.commit()
    await db.refresh(token)
    
    return token, plain_token


async def get_token_by_hash(
    db: AsyncSession,
    token_hash: str
) -> Optional[APIToken]:
    """
    Получение токена по хешу.
    """
    result = await db.execute(
        select(APIToken).where(APIToken.token_hash == token_hash)
    )
    return result.scalar_one_or_none()


async def get_token_by_prefix(
    db: AsyncSession,
    token_prefix: str
) -> Optional[APIToken]:
    """
    Получение токена по префиксу.
    """
    result = await db.execute(
        select(APIToken).where(APIToken.token_prefix == token_prefix)
    )
    return result.scalar_one_or_none()


async def update_token_last_used(
    db: AsyncSession,
    token: APIToken
):
    """
    Обновление времени последнего использования токена.
    """
    token.last_used_at = datetime.now(timezone.utc)
    await db.commit()

