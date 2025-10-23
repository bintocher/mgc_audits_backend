from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets

from app.models.registration_invite import RegistrationInvite


async def create_invite(
    db: AsyncSession,
    email: str,
    created_by_id: Optional[UUID] = None,
    expires_in_hours: int = 72
) -> RegistrationInvite:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
    
    invite = RegistrationInvite(
        email=email,
        token=token,
        expires_at=expires_at,
        created_by_id=created_by_id
    )
    
    db.add(invite)
    await db.commit()
    await db.refresh(invite)
    
    return invite


async def get_invite_by_token(
    db: AsyncSession,
    token: str
) -> Optional[RegistrationInvite]:
    result = await db.execute(
        select(RegistrationInvite).where(RegistrationInvite.token == token)
    )
    return result.scalar_one_or_none()


async def get_invite_by_email(
    db: AsyncSession,
    email: str
) -> Optional[RegistrationInvite]:
    result = await db.execute(
        select(RegistrationInvite).where(RegistrationInvite.email == email)
    )
    return result.scalar_one_or_none()


async def activate_invite(
    db: AsyncSession,
    invite: RegistrationInvite
) -> RegistrationInvite:
    invite.is_activated = True
    await db.commit()
    await db.refresh(invite)
    return invite

