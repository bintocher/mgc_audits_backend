from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_schedule_week import AuditScheduleWeek
from app.schemas.audit_schedule_week import AuditScheduleWeekCreate, AuditScheduleWeekUpdate


async def create_audit_schedule_week(db: AsyncSession, schedule_week: AuditScheduleWeekCreate) -> AuditScheduleWeek:
    db_schedule_week = AuditScheduleWeek(
        audit_id=schedule_week.audit_id,
        week_number=schedule_week.week_number,
        year=schedule_week.year,
        manual_data=schedule_week.manual_data,
        calculated_result=schedule_week.calculated_result,
        calculated_status=schedule_week.calculated_status,
        color_override=schedule_week.color_override
    )
    db.add(db_schedule_week)
    await db.commit()
    await db.refresh(db_schedule_week)
    return db_schedule_week


async def get_audit_schedule_week(db: AsyncSession, schedule_week_id: UUID) -> Optional[AuditScheduleWeek]:
    stmt = select(AuditScheduleWeek).where(AuditScheduleWeek.id == schedule_week_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_audit_schedule_week_by_period(
    db: AsyncSession,
    audit_id: UUID,
    week_number: int,
    year: int
) -> Optional[AuditScheduleWeek]:
    stmt = select(AuditScheduleWeek).where(
        AuditScheduleWeek.audit_id == audit_id,
        AuditScheduleWeek.week_number == week_number,
        AuditScheduleWeek.year == year
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_audit_schedule_weeks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    audit_id: Optional[UUID] = None,
    year: Optional[int] = None,
    week_number: Optional[int] = None
) -> List[AuditScheduleWeek]:
    stmt = select(AuditScheduleWeek)
    
    if audit_id is not None:
        stmt = stmt.where(AuditScheduleWeek.audit_id == audit_id)
    
    if year is not None:
        stmt = stmt.where(AuditScheduleWeek.year == year)
    
    if week_number is not None:
        stmt = stmt.where(AuditScheduleWeek.week_number == week_number)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_audit_schedule_week(
    db: AsyncSession,
    schedule_week_id: UUID,
    schedule_week_update: AuditScheduleWeekUpdate
) -> Optional[AuditScheduleWeek]:
    db_schedule_week = await get_audit_schedule_week(db, schedule_week_id)
    if not db_schedule_week:
        return None
    
    update_data = schedule_week_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_schedule_week, field, value)
    
    await db.commit()
    await db.refresh(db_schedule_week)
    return db_schedule_week


async def update_audit_schedule_week_by_period(
    db: AsyncSession,
    audit_id: UUID,
    week_number: int,
    year: int,
    schedule_week_update: AuditScheduleWeekUpdate
) -> Optional[AuditScheduleWeek]:
    db_schedule_week = await get_audit_schedule_week_by_period(db, audit_id, week_number, year)
    if not db_schedule_week:
        return None
    
    update_data = schedule_week_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_schedule_week, field, value)
    
    await db.commit()
    await db.refresh(db_schedule_week)
    return db_schedule_week


async def delete_audit_schedule_week(db: AsyncSession, schedule_week_id: UUID) -> bool:
    db_schedule_week = await get_audit_schedule_week(db, schedule_week_id)
    if not db_schedule_week:
        return False
    
    db_schedule_week.soft_delete()
    await db.commit()
    return True

