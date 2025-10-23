from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.finding import Finding
from app.models.audit import Audit
from app.models.user import User
from app.models.status import Status
from app.models.dictionary import Dictionary


async def get_findings_report(
    db: AsyncSession,
    enterprise_id: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status_id: Optional[UUID] = None,
    finding_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 1000
) -> tuple[List[dict], int]:
    """
    Получить отчет по несоответствиям.
    
    Returns:
        tuple: (список строк отчета, общее количество)
    """
    stmt = select(
        Finding,
        Audit.audit_number,
        Audit.title.label("audit_title"),
        Dictionary.name.label("process_name"),
        Status.name.label("status_name"),
        User.first_name_ru,
        User.last_name_ru,
        User_approver.first_name_ru.label("approver_first_name"),
        User_approver.last_name_ru.label("approver_last_name")
    ).join(
        Audit, Finding.audit_id == Audit.id
    ).join(
        Dictionary, Finding.process_id == Dictionary.id
    ).join(
        Status, Finding.status_id == Status.id
    ).join(
        User, Finding.resolver_id == User.id
    ).outerjoin(
        User_approver := User.alias(), Finding.approver_id == User_approver.id
    ).where(
        Finding.deleted_at.is_(None)
    )
    
    if enterprise_id:
        stmt = stmt.where(Finding.enterprise_id == enterprise_id)
    
    if date_from:
        stmt = stmt.where(Finding.created_at >= date_from)
    
    if date_to:
        stmt = stmt.where(Finding.created_at <= date_to)
    
    if status_id:
        stmt = stmt.where(Finding.status_id == status_id)
    
    if finding_type:
        stmt = stmt.where(Finding.finding_type == finding_type)
    
    stmt_count = select(func.count()).select_from(stmt.subquery())
    result_count = await db.execute(stmt_count)
    total = result_count.scalar() or 0
    
    stmt = stmt.order_by(Finding.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()
    
    report_data = []
    for row in rows:
        finding = row[0]
        approver_name = None
        if row[8] and row[9]:
            approver_name = f"{row[8]} {row[9]}"
        
        report_data.append({
            "finding_number": finding.finding_number,
            "audit_number": row[1],
            "audit_title": row[2],
            "title": finding.title,
            "finding_type": finding.finding_type,
            "process_name": row[3],
            "status_name": row[4],
            "resolver_name": f"{row[5]} {row[6]}",
            "approver_name": approver_name,
            "deadline": finding.deadline,
            "closing_date": finding.closing_date,
            "created_at": finding.created_at.date()
        })
    
    return report_data, total


async def get_process_report(
    db: AsyncSession,
    enterprise_id: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> List[dict]:
    """
    Получить отчет по процессам.
    
    Returns:
        Список строк отчета
    """
    today = date.today()
    
    stmt = select(
        Dictionary.name.label("process_name"),
        func.count(Finding.id).label("total_findings"),
        func.sum(func.cast(Finding.finding_type == "CAR1", func.Integer)).label("car1_count"),
        func.sum(func.cast(Finding.finding_type == "CAR2", func.Integer)).label("car2_count"),
        func.sum(func.cast(Finding.finding_type == "OFI", func.Integer)).label("ofi_count"),
        func.sum(func.cast(Status.is_final == True, func.Integer)).label("closed_count"),
        func.sum(func.cast(and_(Status.is_final == False, Finding.deadline < today), func.Integer)).label("overdue_count")
    ).join(
        Audit, Finding.audit_id == Audit.id
    ).join(
        Dictionary, Finding.process_id == Dictionary.id
    ).join(
        Status, Finding.status_id == Status.id
    ).where(
        Finding.deleted_at.is_(None)
    ).group_by(
        Dictionary.id, Dictionary.name
    )
    
    if enterprise_id:
        stmt = stmt.where(Finding.enterprise_id == enterprise_id)
    
    if date_from:
        stmt = stmt.where(Finding.created_at >= date_from)
    
    if date_to:
        stmt = stmt.where(Finding.created_at <= date_to)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    report_data = []
    for row in rows:
        report_data.append({
            "process_name": row[0],
            "total_findings": row[1] or 0,
            "car1_count": row[2] or 0,
            "car2_count": row[3] or 0,
            "ofi_count": row[4] or 0,
            "closed_count": row[5] or 0,
            "overdue_count": row[6] or 0
        })
    
    return report_data


async def get_solver_report(
    db: AsyncSession,
    enterprise_id: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> List[dict]:
    """
    Получить отчет по исполнителям.
    
    Returns:
        Список строк отчета
    """
    today = date.today()
    
    stmt = select(
        User.first_name_ru,
        User.last_name_ru,
        func.count(Finding.id).label("total_findings"),
        func.sum(func.cast(Status.is_final == False, func.Integer)).label("active_findings"),
        func.sum(func.cast(and_(Status.is_final == False, Finding.deadline < today), func.Integer)).label("overdue_findings"),
        func.sum(func.cast(Status.is_final == True, func.Integer)).label("closed_findings")
    ).join(
        Audit, Finding.audit_id == Audit.id
    ).join(
        User, Finding.resolver_id == User.id
    ).join(
        Status, Finding.status_id == Status.id
    ).where(
        Finding.deleted_at.is_(None)
    ).group_by(
        User.id, User.first_name_ru, User.last_name_ru
    )
    
    if enterprise_id:
        stmt = stmt.where(Finding.enterprise_id == enterprise_id)
    
    if date_from:
        stmt = stmt.where(Finding.created_at >= date_from)
    
    if date_to:
        stmt = stmt.where(Finding.created_at <= date_to)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    report_data = []
    for row in rows:
        report_data.append({
            "solver_name": f"{row[0]} {row[1]}",
            "total_findings": row[2] or 0,
            "active_findings": row[3] or 0,
            "overdue_findings": row[4] or 0,
            "closed_findings": row[5] or 0
        })
    
    return report_data

