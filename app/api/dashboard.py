from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.crud import dashboard as crud_dashboard
from app.schemas.dashboard import (
    DashboardStatsResponse,
    MyTaskResponse,
    MyTasksDetailResponse
)


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_session)
):
    """
    Получить общую статистику системы для дашборда.
    
    Returns:
        Общая статистика системы:
        - total_audits: Общее количество аудитов
        - total_findings: Общее количество несоответствий
        - active_findings: Количество активных несоответствий
        - overdue_findings: Количество просроченных несоответствий
        - total_users: Общее количество пользователей
        - active_users: Количество активных пользователей
    """
    stats = await crud_dashboard.get_dashboard_stats(db=db)
    return stats


@router.get("/my_tasks", response_model=MyTaskResponse)
async def get_my_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить количество задач текущего пользователя.
    
    Returns:
        Количество задач пользователя:
        - active_findings_count: Количество активных несоответствий пользователя
        - upcoming_audits_count: Количество предстоящих аудитов пользователя
        - overdue_findings_count: Количество просроченных несоответствий пользователя
    """
    counts = await crud_dashboard.get_my_tasks_count(db=db, user_id=current_user.id)
    return counts


@router.get("/my_tasks/detail", response_model=MyTasksDetailResponse)
async def get_my_tasks_detail(
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50, description="Максимальное количество записей для каждого типа задач"),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить детальный список задач текущего пользователя.
    
    Args:
        limit: Максимальное количество записей для каждого типа задач (1-50)
    
    Returns:
        Детальный список задач пользователя:
        - active_findings: Список активных несоответствий
        - upcoming_audits: Список предстоящих аудитов
        - overdue_findings: Список просроченных несоответствий
    """
    tasks = await crud_dashboard.get_my_tasks_detail(db=db, user_id=current_user.id, limit=limit)
    return tasks

