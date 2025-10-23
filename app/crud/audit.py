from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import Audit
from app.schemas.audit import AuditCreate, AuditUpdate


async def create_audit(db: AsyncSession, audit: AuditCreate) -> Audit:
    db_audit = Audit(
        title=audit.title,
        audit_number=audit.audit_number,
        subject=audit.subject,
        enterprise_id=audit.enterprise_id,
        audit_type_id=audit.audit_type_id,
        process_id=audit.process_id,
        product_id=audit.product_id,
        project_id=audit.project_id,
        norm_id=audit.norm_id,
        status_id=audit.status_id,
        auditor_id=audit.auditor_id,
        responsible_user_id=audit.responsible_user_id,
        audit_plan_item_id=audit.audit_plan_item_id,
        audit_date_from=audit.audit_date_from,
        audit_date_to=audit.audit_date_to,
        year=audit.year,
        audit_category=audit.audit_category,
        audit_result=audit.audit_result,
        estimated_hours=audit.estimated_hours,
        actual_hours=audit.actual_hours,
        risk_level_id=audit.risk_level_id,
        milestone_codes=audit.milestone_codes,
        result_comment=audit.result_comment,
        manual_result_value=audit.manual_result_value,
        pcd_planned_close_date=audit.pcd_planned_close_date,
        pcd_actual_close_date=audit.pcd_actual_close_date,
        pcd_status=audit.pcd_status,
        postponed_reason=audit.postponed_reason,
        rescheduled_date=audit.rescheduled_date,
        rescheduled_by_id=audit.rescheduled_by_id,
        rescheduled_at=audit.rescheduled_at,
        approved_by_id=audit.approved_by_id,
        approved_date=audit.approved_date,
        created_by_id=audit.created_by_id
    )
    
    db.add(db_audit)
    await db.flush()
    
    if audit.location_ids:
        from app.models.location import Location
        stmt = select(Location).where(Location.id.in_(audit.location_ids))
        result = await db.execute(stmt)
        locations = result.scalars().all()
        db_audit.locations = locations
    
    if audit.client_ids:
        from app.models.dictionary import Dictionary
        stmt = select(Dictionary).where(Dictionary.id.in_(audit.client_ids))
        result = await db.execute(stmt)
        clients = result.scalars().all()
        db_audit.clients = clients
    
    if audit.shift_ids:
        from app.models.dictionary import Dictionary
        stmt = select(Dictionary).where(Dictionary.id.in_(audit.shift_ids))
        result = await db.execute(stmt)
        shifts = result.scalars().all()
        db_audit.shifts = shifts
    
    await db.commit()
    await db.refresh(db_audit)
    return db_audit


async def get_audit(db: AsyncSession, audit_id: UUID) -> Optional[Audit]:
    stmt = select(Audit).where(Audit.id == audit_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_audits(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    enterprise_id: Optional[UUID] = None,
    audit_category: Optional[str] = None,
    audit_type_id: Optional[UUID] = None,
    status_id: Optional[UUID] = None,
    auditor_id: Optional[UUID] = None,
    year: Optional[int] = None,
    audit_date_from: Optional[datetime] = None,
    audit_date_to: Optional[datetime] = None
) -> List[Audit]:
    stmt = select(Audit)
    
    if enterprise_id is not None:
        stmt = stmt.where(Audit.enterprise_id == enterprise_id)
    
    if audit_category is not None:
        stmt = stmt.where(Audit.audit_category == audit_category)
    
    if audit_type_id is not None:
        stmt = stmt.where(Audit.audit_type_id == audit_type_id)
    
    if status_id is not None:
        stmt = stmt.where(Audit.status_id == status_id)
    
    if auditor_id is not None:
        stmt = stmt.where(Audit.auditor_id == auditor_id)
    
    if year is not None:
        stmt = stmt.where(Audit.year == year)
    
    if audit_date_from is not None:
        stmt = stmt.where(Audit.audit_date_from >= audit_date_from)
    
    if audit_date_to is not None:
        stmt = stmt.where(Audit.audit_date_to <= audit_date_to)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_audit(
    db: AsyncSession,
    audit_id: UUID,
    audit_update: AuditUpdate
) -> Optional[Audit]:
    db_audit = await get_audit(db, audit_id)
    if not db_audit:
        return None
    
    update_data = audit_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field not in ['location_ids', 'client_ids', 'shift_ids']:
            setattr(db_audit, field, value)
    
    if 'location_ids' in update_data and update_data['location_ids'] is not None:
        from app.models.location import Location
        stmt = select(Location).where(Location.id.in_(update_data['location_ids']))
        result = await db.execute(stmt)
        locations = result.scalars().all()
        db_audit.locations = locations
    
    if 'client_ids' in update_data and update_data['client_ids'] is not None:
        from app.models.dictionary import Dictionary
        stmt = select(Dictionary).where(Dictionary.id.in_(update_data['client_ids']))
        result = await db.execute(stmt)
        clients = result.scalars().all()
        db_audit.clients = clients
    
    if 'shift_ids' in update_data and update_data['shift_ids'] is not None:
        from app.models.dictionary import Dictionary
        stmt = select(Dictionary).where(Dictionary.id.in_(update_data['shift_ids']))
        result = await db.execute(stmt)
        shifts = result.scalars().all()
        db_audit.shifts = shifts
    
    await db.commit()
    await db.refresh(db_audit)
    return db_audit


async def delete_audit(db: AsyncSession, audit_id: UUID) -> bool:
    db_audit = await get_audit(db, audit_id)
    if not db_audit:
        return False
    
    db_audit.soft_delete()
    await db.commit()
    return True


async def reschedule_audit(
    db: AsyncSession,
    audit_id: UUID,
    new_date_from: datetime,
    new_date_to: datetime,
    reason: str,
    rescheduled_by_id: UUID
) -> Optional[Audit]:
    db_audit = await get_audit(db, audit_id)
    if not db_audit:
        return None
    
    db_audit.postponed_reason = reason
    db_audit.rescheduled_date = new_date_from
    db_audit.rescheduled_by_id = rescheduled_by_id
    db_audit.rescheduled_at = datetime.now(timezone.utc)
    db_audit.audit_date_from = new_date_from
    db_audit.audit_date_to = new_date_to
    
    await db.commit()
    await db.refresh(db_audit)
    return db_audit


async def get_reschedule_history(
    db: AsyncSession,
    audit_id: UUID
) -> List[dict]:
    """
    Получить историю переносов аудита.
    История содержится в полях rescheduled_date, postponed_reason, rescheduled_by_id, rescheduled_at.
    Возвращает список всех переносов.
    """
    db_audit = await get_audit(db, audit_id)
    if not db_audit:
        return []
    
    if not db_audit.rescheduled_date:
        return []
    
    history = {
        "rescheduled_date": db_audit.rescheduled_date,
        "postponed_reason": db_audit.postponed_reason,
        "rescheduled_by": db_audit.rescheduled_by,
        "rescheduled_at": db_audit.rescheduled_at
    }
    
    return [history]


async def collect_audit_export_data(
    db: AsyncSession,
    audit_id: UUID
) -> dict:
    """
    Собрать все данные аудита для экспорта.
    
    Returns:
        dict: Словарь с данными аудита, findings, attachments, history
    """
    db_audit = await get_audit(db, audit_id)
    if not db_audit:
        return {}
    
    audit_data = {
        "id": str(db_audit.id),
        "title": db_audit.title,
        "audit_number": db_audit.audit_number,
        "subject": db_audit.subject,
        "enterprise_id": str(db_audit.enterprise_id),
        "audit_category": db_audit.audit_category,
        "audit_date_from": db_audit.audit_date_from.isoformat() if db_audit.audit_date_from else None,
        "audit_date_to": db_audit.audit_date_to.isoformat() if db_audit.audit_date_to else None,
        "year": db_audit.year,
        "audit_result": db_audit.audit_result,
        "estimated_hours": float(db_audit.estimated_hours) if db_audit.estimated_hours else None,
        "actual_hours": float(db_audit.actual_hours) if db_audit.actual_hours else None,
        "milestone_codes": db_audit.milestone_codes,
        "result_comment": db_audit.result_comment,
        "created_at": db_audit.created_at.isoformat() if db_audit.created_at else None,
        "updated_at": db_audit.updated_at.isoformat() if db_audit.updated_at else None
    }
    
    findings_data = []
    if db_audit.findings:
        for finding in db_audit.findings:
            findings_data.append({
                "finding_number": finding.finding_number,
                "title": finding.title,
                "description": finding.description,
                "finding_type": finding.finding_type,
                "deadline": finding.deadline.isoformat() if finding.deadline else None,
                "closing_date": finding.closing_date.isoformat() if finding.closing_date else None,
                "why_1": finding.why_1,
                "why_2": finding.why_2,
                "why_3": finding.why_3,
                "why_4": finding.why_4,
                "why_5": finding.why_5,
                "immediate_action": finding.immediate_action,
                "root_cause": finding.root_cause,
                "long_term_action": finding.long_term_action,
                "action_verification": finding.action_verification,
                "preventive_measures": finding.preventive_measures
            })
    
    attachments_data = []
    history_data = []
    
    return {
        "audit": audit_data,
        "findings": findings_data,
        "attachments": attachments_data,
        "history": history_data
    }

