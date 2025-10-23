from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.status_transition import StatusTransition


async def get_transition(
    db: AsyncSession,
    transition_id: UUID
) -> Optional[StatusTransition]:
    result = await db.execute(
        select(StatusTransition).where(StatusTransition.id == transition_id)
    )
    return result.scalar_one_or_none()


async def get_transitions_from_status(
    db: AsyncSession,
    from_status_id: UUID
) -> List[StatusTransition]:
    result = await db.execute(
        select(StatusTransition).where(StatusTransition.from_status_id == from_status_id)
    )
    return list(result.scalars().all())


async def get_transition_between_statuses(
    db: AsyncSession,
    from_status_id: UUID,
    to_status_id: UUID
) -> Optional[StatusTransition]:
    result = await db.execute(
        select(StatusTransition)
        .where(StatusTransition.from_status_id == from_status_id)
        .where(StatusTransition.to_status_id == to_status_id)
    )
    return result.scalar_one_or_none()


async def get_all_transitions(
    db: AsyncSession
) -> List[StatusTransition]:
    result = await db.execute(select(StatusTransition))
    return list(result.scalars().all())

