from typing import List, Optional, Dict
from uuid import UUID
from datetime import date, datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.audit import Audit
from app.models.audit_schedule_week import AuditScheduleWeek
from app.models.user import User
from app.models.location import Location
from app.models.dictionary import Dictionary


def get_weeks_in_range(date_from: date, date_to: date) -> List[Dict]:
    """
    Вычислить список недель в заданном диапазоне дат.
    
    Args:
        date_from: Начальная дата
        date_to: Конечная дата
    
    Returns:
        Список словарей с информацией о неделях (week_number, year, start_date, end_date)
    """
    weeks = []
    current_date = date_from
    
    while current_date <= date_to:
        year = current_date.year
        week_number = current_date.isocalendar()[1]
        
        monday = current_date - timedelta(days=current_date.weekday())
        sunday = monday + timedelta(days=6)
        
        if sunday > date_to:
            sunday = date_to
        
        weeks.append({
            "week_number": week_number,
            "year": year,
            "start_date": monday,
            "end_date": sunday
        })
        
        current_date = sunday + timedelta(days=1)
    
    return weeks


def calculate_color(audit_result: Optional[str], status_code: Optional[str]) -> str:
    """
    Вычислить цвет ячейки графика на основе результата аудита и статуса.
    
    Args:
        audit_result: Результат аудита ('green', 'yellow', 'red', 'no_noncompliance')
        status_code: Код статуса
    
    Returns:
        HEX цвет (#RRGGBB)
    """
    if audit_result == 'green':
        return '#00FF00'
    elif audit_result == 'yellow':
        return '#FFFF00'
    elif audit_result == 'red':
        return '#FF0000'
    elif audit_result == 'no_noncompliance':
        return '#90EE90'
    else:
        return '#CCCCCC'


async def auto_fill_schedule_weeks(
    db: AsyncSession,
    audit_id: UUID,
    audit_date_from: date,
    audit_date_to: date
) -> List[AuditScheduleWeek]:
    """
    Автоматически заполнить ячейки графика на основе дат аудита.
    
    Args:
        db: Сессия базы данных
        audit_id: ID аудита
        audit_date_from: Начальная дата аудита
        audit_date_to: Конечная дата аудита
    
    Returns:
        Список созданных ячеек графика
    """
    weeks = get_weeks_in_range(audit_date_from, audit_date_to)
    year = audit_date_from.year
    
    created_weeks = []
    
    for week_info in weeks:
        existing_week = await db.execute(
            select(AuditScheduleWeek).where(
                and_(
                    AuditScheduleWeek.audit_id == audit_id,
                    AuditScheduleWeek.week_number == week_info['week_number'],
                    AuditScheduleWeek.year == week_info['year']
                )
            )
        )
        
        if existing_week.scalar_one_or_none() is None:
            schedule_week = AuditScheduleWeek(
                audit_id=audit_id,
                week_number=week_info['week_number'],
                year=week_info['year']
            )
            db.add(schedule_week)
            created_weeks.append(schedule_week)
    
    await db.commit()
    
    for week in created_weeks:
        await db.refresh(week)
    
    return created_weeks


async def get_audit_schedule(
    db: AsyncSession,
    date_from: date,
    date_to: date,
    audit_category: Optional[str] = None,
    enterprise_id: Optional[UUID] = None,
    division_id: Optional[UUID] = None,
    auditor_id: Optional[UUID] = None,
    status_id: Optional[UUID] = None
) -> List[Audit]:
    """
    Получить список аудитов для графика за указанный период.
    
    Args:
        db: Сессия базы данных
        date_from: Начальная дата периода
        date_to: Конечная дата периода
        audit_category: Фильтр по категории
        enterprise_id: Фильтр по предприятию
        division_id: Фильтр по дивизиону
        auditor_id: Фильтр по аудитору
        status_id: Фильтр по статусу
    
    Returns:
        Список аудитов с загруженными связанными данными
    """
    stmt = select(Audit).where(
        and_(
            Audit.audit_date_from <= date_to,
            Audit.audit_date_to >= date_from
        )
    )
    
    if audit_category:
        stmt = stmt.where(Audit.audit_category == audit_category)
    
    if enterprise_id:
        stmt = stmt.where(Audit.enterprise_id == enterprise_id)
    
    if auditor_id:
        stmt = stmt.where(Audit.auditor_id == auditor_id)
    
    if status_id:
        stmt = stmt.where(Audit.status_id == status_id)
    
    stmt = stmt.options(
        selectinload(Audit.auditor),
        selectinload(Audit.locations),
        selectinload(Audit.clients),
        selectinload(Audit.status),
        selectinload(Audit.schedule_weeks)
    )
    
    result = await db.execute(stmt)
    audits = list(result.scalars().all())
    
    for audit in audits:
        await auto_fill_schedule_weeks(db, audit.id, audit.audit_date_from, audit.audit_date_to)
    
    return audits


async def get_audit_schedule_by_component(
    db: AsyncSession,
    date_from: date,
    date_to: date,
    component_type: Optional[str] = None,
    sap_id: Optional[str] = None,
    enterprise_id: Optional[UUID] = None
) -> List[Dict]:
    """
    Получить график аудитов по компонентам.
    
    Args:
        db: Сессия базы данных
        date_from: Начальная дата периода
        date_to: Конечная дата периода
        component_type: Фильтр по типу компонента
        sap_id: Фильтр по SAP ID
        enterprise_id: Фильтр по предприятию
    
    Returns:
        Список компонентов с информацией об аудитах
    """
    from app.models.audit_component import AuditComponent
    
    stmt = select(AuditComponent).join(Audit).where(
        and_(
            Audit.audit_date_from <= date_to,
            Audit.audit_date_to >= date_from
        )
    )
    
    if component_type:
        stmt = stmt.where(AuditComponent.component_type == component_type)
    
    if sap_id:
        stmt = stmt.where(AuditComponent.sap_id == sap_id)
    
    if enterprise_id:
        stmt = stmt.where(Audit.enterprise_id == enterprise_id)
    
    stmt = stmt.options(
        selectinload(AuditComponent.audit).selectinload(Audit.status)
    )
    
    result = await db.execute(stmt)
    components = result.scalars().all()
    
    schedule_items = []
    for component in components:
        schedule_items.append({
            "component_type": component.component_type,
            "sap_id": component.sap_id,
            "part_number": component.part_number,
            "component_name": component.component_name,
            "audit_date_from": component.audit.audit_date_from,
            "audit_date_to": component.audit.audit_date_to,
            "estimated_hours": component.audit.estimated_hours,
            "actual_hours": component.audit.actual_hours,
            "status": component.audit.status
        })
    
    return schedule_items

