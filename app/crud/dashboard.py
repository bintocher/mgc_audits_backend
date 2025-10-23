from typing import List
from uuid import UUID
from datetime import date, datetime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.finding import Finding
from app.models.audit import Audit
from app.models.user import User
from app.models.status import Status


async def get_dashboard_stats(db: AsyncSession) -> dict:
    """
    Получить общую статистику системы для дашборда.
    
    Returns:
        dict: Словарь со статистикой
    """
    today = date.today()
    
    stmt_total_audits = select(func.count(Audit.id))
    result_total_audits = await db.execute(stmt_total_audits)
    total_audits = result_total_audits.scalar() or 0
    
    stmt_total_findings = select(func.count(Finding.id))
    result_total_findings = await db.execute(stmt_total_findings)
    total_findings = result_total_findings.scalar() or 0
    
    stmt_active_findings = select(func.count(Finding.id)).join(
        Status, Finding.status_id == Status.id
    ).where(
        and_(
            Status.is_final == False,
            Finding.deleted_at.is_(None)
        )
    )
    result_active_findings = await db.execute(stmt_active_findings)
    active_findings = result_active_findings.scalar() or 0
    
    stmt_overdue_findings = select(func.count(Finding.id)).join(
        Status, Finding.status_id == Status.id
    ).where(
        and_(
            Status.is_final == False,
            Finding.deadline < today,
            Finding.deleted_at.is_(None)
        )
    )
    result_overdue_findings = await db.execute(stmt_overdue_findings)
    overdue_findings = result_overdue_findings.scalar() or 0
    
    stmt_total_users = select(func.count(User.id))
    result_total_users = await db.execute(stmt_total_users)
    total_users = result_total_users.scalar() or 0
    
    stmt_active_users = select(func.count(User.id)).where(
        and_(
            User.is_active == True,
            User.deleted_at.is_(None)
        )
    )
    result_active_users = await db.execute(stmt_active_users)
    active_users = result_active_users.scalar() or 0
    
    return {
        "total_audits": total_audits,
        "total_findings": total_findings,
        "active_findings": active_findings,
        "overdue_findings": overdue_findings,
        "total_users": total_users,
        "active_users": active_users
    }


async def get_my_tasks_count(db: AsyncSession, user_id: UUID) -> dict:
    """
    Получить количество задач текущего пользователя.
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
    
    Returns:
        dict: Словарь с количеством задач
    """
    today = date.today()
    
    stmt_active_findings = select(func.count(Finding.id)).join(
        Status, Finding.status_id == Status.id
    ).where(
        and_(
            Finding.resolver_id == user_id,
            Status.is_final == False,
            Finding.deleted_at.is_(None)
        )
    )
    result_active_findings = await db.execute(stmt_active_findings)
    active_findings_count = result_active_findings.scalar() or 0
    
    stmt_upcoming_audits = select(func.count(Audit.id)).join(
        Status, Audit.status_id == Status.id
    ).where(
        and_(
            Audit.auditor_id == user_id,
            Audit.audit_date_from >= today,
            Status.is_final == False,
            Audit.deleted_at.is_(None)
        )
    )
    result_upcoming_audits = await db.execute(stmt_upcoming_audits)
    upcoming_audits_count = result_upcoming_audits.scalar() or 0
    
    stmt_overdue_findings = select(func.count(Finding.id)).join(
        Status, Finding.status_id == Status.id
    ).where(
        and_(
            Finding.resolver_id == user_id,
            Status.is_final == False,
            Finding.deadline < today,
            Finding.deleted_at.is_(None)
        )
    )
    result_overdue_findings = await db.execute(stmt_overdue_findings)
    overdue_findings_count = result_overdue_findings.scalar() or 0
    
    return {
        "active_findings_count": active_findings_count,
        "upcoming_audits_count": upcoming_audits_count,
        "overdue_findings_count": overdue_findings_count
    }


async def get_my_tasks_detail(db: AsyncSession, user_id: UUID, limit: int = 10) -> dict:
    """
    Получить детальный список задач текущего пользователя.
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        limit: Максимальное количество записей для каждого типа задач
    
    Returns:
        dict: Словарь со списками задач
    """
    today = date.today()
    
    stmt_active_findings = select(Finding, Status.code.label("status_code")).join(
        Status, Finding.status_id == Status.id
    ).join(
        Audit, Finding.audit_id == Audit.id
    ).where(
        and_(
            Finding.resolver_id == user_id,
            Status.is_final == False,
            Finding.deleted_at.is_(None)
        )
    ).order_by(Finding.deadline.asc()).limit(limit)
    
    result_active_findings = await db.execute(stmt_active_findings)
    active_findings_rows = result_active_findings.all()
    
    active_findings = []
    for finding, status_code in active_findings_rows:
        active_findings.append({
            "id": finding.id,
            "finding_number": finding.finding_number,
            "title": finding.title,
            "deadline": finding.deadline,
            "status": status_code,
            "audit_title": finding.audit.title
        })
    
    stmt_upcoming_audits = select(Audit, Status.code.label("status_code")).join(
        Status, Audit.status_id == Status.id
    ).where(
        and_(
            Audit.auditor_id == user_id,
            Audit.audit_date_from >= today,
            Status.is_final == False,
            Audit.deleted_at.is_(None)
        )
    ).order_by(Audit.audit_date_from.asc()).limit(limit)
    
    result_upcoming_audits = await db.execute(stmt_upcoming_audits)
    upcoming_audits_rows = result_upcoming_audits.all()
    
    upcoming_audits = []
    for audit, status_code in upcoming_audits_rows:
        upcoming_audits.append({
            "id": audit.id,
            "audit_number": audit.audit_number,
            "title": audit.title,
            "audit_date_from": audit.audit_date_from,
            "audit_date_to": audit.audit_date_to,
            "status": status_code
        })
    
    stmt_overdue_findings = select(Finding, Status.code.label("status_code")).join(
        Status, Finding.status_id == Status.id
    ).join(
        Audit, Finding.audit_id == Audit.id
    ).where(
        and_(
            Finding.resolver_id == user_id,
            Status.is_final == False,
            Finding.deadline < today,
            Finding.deleted_at.is_(None)
        )
    ).order_by(Finding.deadline.asc()).limit(limit)
    
    result_overdue_findings = await db.execute(stmt_overdue_findings)
    overdue_findings_rows = result_overdue_findings.all()
    
    overdue_findings = []
    for finding, status_code in overdue_findings_rows:
        overdue_findings.append({
            "id": finding.id,
            "finding_number": finding.finding_number,
            "title": finding.title,
            "deadline": finding.deadline,
            "status": status_code,
            "audit_title": finding.audit.title
        })
    
    return {
        "active_findings": active_findings,
        "upcoming_audits": upcoming_audits,
        "overdue_findings": overdue_findings
    }

