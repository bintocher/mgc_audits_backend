from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.status import Status


async def get_status(
    db: AsyncSession,
    status_id: UUID
) -> Optional[Status]:
    result = await db.execute(
        select(Status).where(Status.id == status_id)
    )
    return result.scalar_one_or_none()


async def get_statuses_by_entity_type(
    db: AsyncSession,
    entity_type: str
) -> List[Status]:
    result = await db.execute(
        select(Status)
        .where(Status.entity_type == entity_type)
        .order_by(Status.order)
    )
    return list(result.scalars().all())


async def get_initial_status(
    db: AsyncSession,
    entity_type: str
) -> Optional[Status]:
    result = await db.execute(
        select(Status)
        .where(Status.entity_type == entity_type)
        .where(Status.is_initial == True)
    )
    return result.scalar_one_or_none()


async def get_final_statuses(
    db: AsyncSession,
    entity_type: str
) -> List[Status]:
    result = await db.execute(
        select(Status)
        .where(Status.entity_type == entity_type)
        .where(Status.is_final == True)
    )
    return list(result.scalars().all())

