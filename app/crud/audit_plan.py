from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_plan import AuditPlan
from app.models.audit_plan_item import AuditPlanItem
from app.schemas.audit_plan import AuditPlanCreate, AuditPlanUpdate


async def create_audit_plan(db: AsyncSession, audit_plan: AuditPlanCreate) -> AuditPlan:
    db_audit_plan = AuditPlan(
        title=audit_plan.title,
        date_from=audit_plan.date_from,
        date_to=audit_plan.date_to,
        enterprise_id=audit_plan.enterprise_id,
        category=audit_plan.category,
        status=audit_plan.status,
        version_number=audit_plan.version_number,
        created_by_id=audit_plan.created_by_id
    )
    db.add(db_audit_plan)
    await db.commit()
    await db.refresh(db_audit_plan)
    return db_audit_plan


async def get_audit_plan(db: AsyncSession, audit_plan_id: UUID) -> Optional[AuditPlan]:
    stmt = select(AuditPlan).where(AuditPlan.id == audit_plan_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_audit_plans(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    enterprise_id: Optional[UUID] = None,
    category: Optional[str] = None,
    status: Optional[str] = None
) -> List[AuditPlan]:
    stmt = select(AuditPlan)
    
    if enterprise_id is not None:
        stmt = stmt.where(AuditPlan.enterprise_id == enterprise_id)
    
    if category is not None:
        stmt = stmt.where(AuditPlan.category == category)
    
    if status is not None:
        stmt = stmt.where(AuditPlan.status == status)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_audit_plan(
    db: AsyncSession,
    audit_plan_id: UUID,
    audit_plan_update: AuditPlanUpdate
) -> Optional[AuditPlan]:
    db_audit_plan = await get_audit_plan(db, audit_plan_id)
    if not db_audit_plan:
        return None
    
    update_data = audit_plan_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_audit_plan, field, value)
    
    await db.commit()
    await db.refresh(db_audit_plan)
    return db_audit_plan


async def delete_audit_plan(db: AsyncSession, audit_plan_id: UUID) -> bool:
    db_audit_plan = await get_audit_plan(db, audit_plan_id)
    if not db_audit_plan:
        return False
    
    db_audit_plan.soft_delete()
    await db.commit()
    return True


async def approve_by_division(
    db: AsyncSession,
    audit_plan_id: UUID,
    approver_id: UUID
) -> Optional[AuditPlan]:
    db_audit_plan = await get_audit_plan(db, audit_plan_id)
    if not db_audit_plan:
        return None
    
    db_audit_plan.approved_by_division = True
    db_audit_plan.approved_by_division_user_id = approver_id
    db_audit_plan.approved_by_division_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(db_audit_plan)
    return db_audit_plan


async def approve_by_uk(
    db: AsyncSession,
    audit_plan_id: UUID,
    approver_id: UUID
) -> Optional[AuditPlan]:
    db_audit_plan = await get_audit_plan(db, audit_plan_id)
    if not db_audit_plan:
        return None
    
    db_audit_plan.approved_by_uk = True
    db_audit_plan.approved_by_uk_user_id = approver_id
    db_audit_plan.approved_by_uk_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(db_audit_plan)
    return db_audit_plan


async def reject_audit_plan(
    db: AsyncSession,
    audit_plan_id: UUID,
    reason: str
) -> Optional[AuditPlan]:
    db_audit_plan = await get_audit_plan(db, audit_plan_id)
    if not db_audit_plan:
        return None
    
    db_audit_plan.approved_by_division = False
    db_audit_plan.approved_by_division_user_id = None
    db_audit_plan.approved_by_division_at = None
    db_audit_plan.approved_by_uk = False
    db_audit_plan.approved_by_uk_user_id = None
    db_audit_plan.approved_by_uk_at = None
    db_audit_plan.status = 'draft'
    
    await db.commit()
    await db.refresh(db_audit_plan)
    return db_audit_plan


async def create_audit_plan_item(db: AsyncSession, audit_plan_item: dict) -> AuditPlanItem:
    db_audit_plan_item = AuditPlanItem(**audit_plan_item)
    db.add(db_audit_plan_item)
    await db.commit()
    await db.refresh(db_audit_plan_item)
    return db_audit_plan_item


async def get_audit_plan_item(db: AsyncSession, audit_plan_item_id: UUID) -> Optional[AuditPlanItem]:
    stmt = select(AuditPlanItem).where(AuditPlanItem.id == audit_plan_item_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_audit_plan_items(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    audit_plan_id: Optional[UUID] = None,
    planned_auditor_id: Optional[UUID] = None
) -> List[AuditPlanItem]:
    stmt = select(AuditPlanItem)
    
    if audit_plan_id is not None:
        stmt = stmt.where(AuditPlanItem.audit_plan_id == audit_plan_id)
    
    if planned_auditor_id is not None:
        stmt = stmt.where(AuditPlanItem.planned_auditor_id == planned_auditor_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_audit_plan_item(
    db: AsyncSession,
    audit_plan_item_id: UUID,
    audit_plan_item_update: dict
) -> Optional[AuditPlanItem]:
    db_audit_plan_item = await get_audit_plan_item(db, audit_plan_item_id)
    if not db_audit_plan_item:
        return None
    
    for field, value in audit_plan_item_update.items():
        setattr(db_audit_plan_item, field, value)
    
    await db.commit()
    await db.refresh(db_audit_plan_item)
    return db_audit_plan_item


async def delete_audit_plan_item(db: AsyncSession, audit_plan_item_id: UUID) -> bool:
    db_audit_plan_item = await get_audit_plan_item(db, audit_plan_item_id)
    if not db_audit_plan_item:
        return False
    
    db_audit_plan_item.soft_delete()
    await db.commit()
    return True

