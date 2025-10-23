from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.finding_delegation import FindingDelegation
from app.schemas.finding import FindingDelegationCreate


async def create_finding_delegation(db: AsyncSession, delegation: FindingDelegationCreate) -> FindingDelegation:
    db_delegation = FindingDelegation(
        finding_id=delegation.finding_id,
        from_user_id=delegation.from_user_id,
        to_user_id=delegation.to_user_id,
        reason=delegation.reason,
        delegated_at=datetime.now(timezone.utc)
    )
    
    db.add(db_delegation)
    await db.commit()
    await db.refresh(db_delegation)
    return db_delegation


async def get_finding_delegation(db: AsyncSession, delegation_id: UUID) -> Optional[FindingDelegation]:
    stmt = select(FindingDelegation).where(FindingDelegation.id == delegation_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_finding_delegations(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    finding_id: Optional[UUID] = None
) -> List[FindingDelegation]:
    stmt = select(FindingDelegation)
    
    if finding_id is not None:
        stmt = stmt.where(FindingDelegation.finding_id == finding_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def revoke_finding_delegation(db: AsyncSession, delegation_id: UUID) -> Optional[FindingDelegation]:
    db_delegation = await get_finding_delegation(db, delegation_id)
    if not db_delegation:
        return None
    
    db_delegation.revoked_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(db_delegation)
    return db_delegation

