from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.finding import Finding
from app.schemas.finding import FindingCreate, FindingUpdate


async def create_finding(db: AsyncSession, finding: FindingCreate) -> Finding:
    db_finding = Finding(
        audit_id=finding.audit_id,
        enterprise_id=finding.enterprise_id,
        title=finding.title,
        description=finding.description,
        process_id=finding.process_id,
        status_id=finding.status_id,
        finding_type=finding.finding_type,
        resolver_id=finding.resolver_id,
        approver_id=finding.approver_id,
        deadline=finding.deadline,
        why_1=finding.why_1,
        why_2=finding.why_2,
        why_3=finding.why_3,
        why_4=finding.why_4,
        why_5=finding.why_5,
        immediate_action=finding.immediate_action,
        root_cause=finding.root_cause,
        long_term_action=finding.long_term_action,
        action_verification=finding.action_verification,
        preventive_measures=finding.preventive_measures,
        created_by_id=finding.created_by_id
    )
    
    db.add(db_finding)
    await db.flush()
    
    stmt = select(func.max(Finding.finding_number))
    result = await db.execute(stmt)
    max_number = result.scalar()
    
    if max_number is None:
        db_finding.finding_number = 1
    else:
        db_finding.finding_number = max_number + 1
    
    await db.commit()
    await db.refresh(db_finding)
    return db_finding


async def get_finding(db: AsyncSession, finding_id: UUID) -> Optional[Finding]:
    stmt = select(Finding).where(Finding.id == finding_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_findings(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    audit_id: Optional[UUID] = None,
    enterprise_id: Optional[UUID] = None,
    status_id: Optional[UUID] = None,
    resolver_id: Optional[UUID] = None,
    approver_id: Optional[UUID] = None,
    deadline_from: Optional[date] = None,
    deadline_to: Optional[date] = None
) -> List[Finding]:
    stmt = select(Finding)
    
    if audit_id is not None:
        stmt = stmt.where(Finding.audit_id == audit_id)
    
    if enterprise_id is not None:
        stmt = stmt.where(Finding.enterprise_id == enterprise_id)
    
    if status_id is not None:
        stmt = stmt.where(Finding.status_id == status_id)
    
    if resolver_id is not None:
        stmt = stmt.where(Finding.resolver_id == resolver_id)
    
    if approver_id is not None:
        stmt = stmt.where(Finding.approver_id == approver_id)
    
    if deadline_from is not None:
        stmt = stmt.where(Finding.deadline >= deadline_from)
    
    if deadline_to is not None:
        stmt = stmt.where(Finding.deadline <= deadline_to)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_finding(
    db: AsyncSession,
    finding_id: UUID,
    finding_update: FindingUpdate
) -> Optional[Finding]:
    db_finding = await get_finding(db, finding_id)
    if not db_finding:
        return None
    
    update_data = finding_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_finding, field, value)
    
    await db.commit()
    await db.refresh(db_finding)
    return db_finding


async def delete_finding(db: AsyncSession, finding_id: UUID) -> bool:
    db_finding = await get_finding(db, finding_id)
    if not db_finding:
        return False
    
    db_finding.soft_delete()
    await db.commit()
    return True

