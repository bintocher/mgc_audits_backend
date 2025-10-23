from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.crud import notification as crud_notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationStatsResponse,
    NotificationQueueResponse,
    NotificationQueueStatsResponse
)


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    event_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    is_read: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список уведомлений текущего пользователя.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        event_type: Фильтр по типу события
        entity_type: Фильтр по типу сущности
        entity_id: Фильтр по ID сущности
        is_read: Фильтр по статусу прочтения
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Список уведомлений
    """
    notifications = await crud_notification.get_notifications(
        db=db,
        skip=skip,
        limit=limit,
        user_id=current_user.id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        is_read=is_read
    )
    return notifications


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_notification_stats(
    days: int = Query(7, ge=1, le=7),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить статистику уведомлений.
    
    Args:
        days: Количество дней для статистики (1-7)
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Статистика уведомлений
    """
    stats = await crud_notification.get_notification_stats(
        db=db,
        user_id=current_user.id,
        days=days
    )
    return stats


@router.post("/read_all", status_code=status.HTTP_200_OK)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Отметить все уведомления как прочитанные.
    
    Args:
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Количество обновленных уведомлений
    """
    count = await crud_notification.mark_all_notifications_as_read(
        db=db,
        user_id=current_user.id
    )
    return {"count": count}


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Отметить уведомление как прочитанное.
    
    Args:
        notification_id: ID уведомления
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Обновленное уведомление
    
    Raises:
        HTTPException: Если уведомление не найдено или не принадлежит пользователю
    """
    notification = await crud_notification.get_notification(db=db, notification_id=notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено"
        )
    
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому уведомлению"
        )
    
    updated_notification = await crud_notification.mark_notification_as_read(
        db=db,
        notification_id=notification_id
    )
    
    return updated_notification


@router.get("/queue/stats", response_model=NotificationQueueStatsResponse)
async def get_notification_queue_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить статистику очереди уведомлений.
    
    Args:
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Статистика очереди уведомлений
    
    Raises:
        HTTPException: Если пользователь не имеет прав администратора
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра статистики очереди"
        )
    
    stats = await crud_notification.get_notification_queue_stats(db=db)
    return stats


@router.get("/queue", response_model=List[NotificationQueueResponse])
async def get_notification_queue(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    notification_id: Optional[UUID] = None,
    channel: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список элементов очереди уведомлений.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        notification_id: Фильтр по ID уведомления
        channel: Фильтр по каналу
        status: Фильтр по статусу
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Список элементов очереди
    
    Raises:
        HTTPException: Если пользователь не имеет прав администратора
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра очереди"
        )
    
    queue_items = await crud_notification.get_notification_queue_list(
        db=db,
        skip=skip,
        limit=limit,
        notification_id=notification_id,
        channel=channel,
        status=status
    )
    return queue_items


@router.get("/failed", response_model=List[NotificationResponse])
async def get_failed_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список неудачных уведомлений.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Список неудачных уведомлений
    
    Raises:
        HTTPException: Если пользователь не имеет прав администратора
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра неудачных уведомлений"
        )
    
    notifications = await crud_notification.get_notifications(
        db=db,
        skip=skip,
        limit=limit,
        user_id=None
    )
    
    failed_notifications = [
        n for n in notifications 
        if n.email_error or n.telegram_error
    ]
    
    return failed_notifications[:limit]

