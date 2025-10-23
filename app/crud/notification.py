from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.models.notification_queue import NotificationQueue
from app.schemas.notification import NotificationCreate, NotificationUpdate


async def create_notification(db: AsyncSession, notification: NotificationCreate) -> Notification:
    db_notification = Notification(
        user_id=notification.user_id,
        event_type=notification.event_type,
        entity_type=notification.entity_type,
        entity_id=notification.entity_id,
        title=notification.title,
        message=notification.message,
        notification_config=notification.notification_config
    )
    
    db.add(db_notification)
    await db.commit()
    await db.refresh(db_notification)
    return db_notification


async def get_notification(db: AsyncSession, notification_id: UUID) -> Optional[Notification]:
    stmt = select(Notification).where(Notification.id == notification_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_notifications(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[UUID] = None,
    event_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    is_read: Optional[bool] = None
) -> List[Notification]:
    stmt = select(Notification)
    
    if user_id is not None:
        stmt = stmt.where(Notification.user_id == user_id)
    
    if event_type is not None:
        stmt = stmt.where(Notification.event_type == event_type)
    
    if entity_type is not None:
        stmt = stmt.where(Notification.entity_type == entity_type)
    
    if entity_id is not None:
        stmt = stmt.where(Notification.entity_id == entity_id)
    
    if is_read is not None:
        stmt = stmt.where(Notification.is_read == is_read)
    
    stmt = stmt.order_by(Notification.created_at.desc())
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_notification(
    db: AsyncSession,
    notification_id: UUID,
    notification_update: NotificationUpdate
) -> Optional[Notification]:
    db_notification = await get_notification(db, notification_id)
    if not db_notification:
        return None
    
    update_data = notification_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_notification, field, value)
    
    await db.commit()
    await db.refresh(db_notification)
    return db_notification


async def mark_notification_as_read(db: AsyncSession, notification_id: UUID) -> Optional[Notification]:
    db_notification = await get_notification(db, notification_id)
    if not db_notification:
        return None
    
    db_notification.is_read = True
    await db.commit()
    await db.refresh(db_notification)
    return db_notification


async def mark_all_notifications_as_read(db: AsyncSession, user_id: UUID) -> int:
    stmt = select(Notification).where(
        and_(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    )
    result = await db.execute(stmt)
    notifications = result.scalars().all()
    
    count = 0
    for notification in notifications:
        notification.is_read = True
        count += 1
    
    await db.commit()
    return count


async def delete_notification(db: AsyncSession, notification_id: UUID) -> bool:
    db_notification = await get_notification(db, notification_id)
    if not db_notification:
        return False
    
    db_notification.soft_delete()
    await db.commit()
    return True


async def get_notification_stats(
    db: AsyncSession,
    user_id: Optional[UUID] = None,
    days: int = 7
) -> Dict[str, Any]:
    date_from = datetime.now() - timedelta(days=days)
    
    stmt = select(Notification).where(Notification.created_at >= date_from)
    
    if user_id is not None:
        stmt = stmt.where(Notification.user_id == user_id)
    
    result = await db.execute(stmt)
    notifications = result.scalars().all()
    
    stats = {
        "total_notifications": len(notifications),
        "unread_notifications": sum(1 for n in notifications if not n.is_read),
        "email_sent": sum(1 for n in notifications if n.sent_email),
        "telegram_sent": sum(1 for n in notifications if n.sent_telegram),
        "failed_email": sum(1 for n in notifications if n.email_error),
        "failed_telegram": sum(1 for n in notifications if n.telegram_error),
        "by_event_type": {},
        "by_channel": {}
    }
    
    for notification in notifications:
        event_type = notification.event_type
        stats["by_event_type"][event_type] = stats["by_event_type"].get(event_type, 0) + 1
        
        if notification.sent_email:
            stats["by_channel"]["email"] = stats["by_channel"].get("email", 0) + 1
        if notification.sent_telegram:
            stats["by_channel"]["telegram"] = stats["by_channel"].get("telegram", 0) + 1
    
    return stats


async def create_notification_queue(db: AsyncSession, queue_item: Dict[str, Any]) -> NotificationQueue:
    db_queue = NotificationQueue(
        notification_id=queue_item["notification_id"],
        channel=queue_item["channel"],
        status=queue_item["status"],
        priority=queue_item.get("priority", 0),
        scheduled_at=queue_item["scheduled_at"],
        retry_count=queue_item.get("retry_count", 0),
        max_retries=queue_item.get("max_retries", 3)
    )
    
    db.add(db_queue)
    await db.commit()
    await db.refresh(db_queue)
    return db_queue


async def get_notification_queue(db: AsyncSession, queue_id: UUID) -> Optional[NotificationQueue]:
    stmt = select(NotificationQueue).where(NotificationQueue.id == queue_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_notification_queue_list(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    notification_id: Optional[UUID] = None,
    channel: Optional[str] = None,
    status: Optional[str] = None
) -> List[NotificationQueue]:
    stmt = select(NotificationQueue)
    
    if notification_id is not None:
        stmt = stmt.where(NotificationQueue.notification_id == notification_id)
    
    if channel is not None:
        stmt = stmt.where(NotificationQueue.channel == channel)
    
    if status is not None:
        stmt = stmt.where(NotificationQueue.status == status)
    
    stmt = stmt.order_by(NotificationQueue.created_at.desc())
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_notification_queue(
    db: AsyncSession,
    queue_id: UUID,
    queue_update: Dict[str, Any]
) -> Optional[NotificationQueue]:
    db_queue = await get_notification_queue(db, queue_id)
    if not db_queue:
        return None
    
    for field, value in queue_update.items():
        setattr(db_queue, field, value)
    
    await db.commit()
    await db.refresh(db_queue)
    return db_queue


async def get_pending_notifications(db: AsyncSession, limit: int = 100) -> List[NotificationQueue]:
    stmt = select(NotificationQueue).where(
        and_(
            NotificationQueue.status == "pending",
            NotificationQueue.scheduled_at <= datetime.now()
        )
    ).order_by(NotificationQueue.priority.desc(), NotificationQueue.scheduled_at.asc()).limit(limit)
    
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_notification_queue_stats(db: AsyncSession) -> Dict[str, Any]:
    stmt = select(NotificationQueue)
    result = await db.execute(stmt)
    queues = result.scalars().all()
    
    stats = {
        "pending": sum(1 for q in queues if q.status == "pending"),
        "processing": sum(1 for q in queues if q.status == "processing"),
        "failed": sum(1 for q in queues if q.status == "failed"),
        "size": len(queues),
        "lag_minutes": None,
        "speed_per_minute": None
    }
    
    if queues:
        oldest_pending = min((q for q in queues if q.status == "pending"), 
                            key=lambda q: q.scheduled_at, default=None)
        if oldest_pending:
            lag = datetime.now() - oldest_pending.scheduled_at
            stats["lag_minutes"] = lag.total_seconds() / 60
    
    return stats


async def delete_notification_queue(db: AsyncSession, queue_id: UUID) -> bool:
    db_queue = await get_notification_queue(db, queue_id)
    if not db_queue:
        return False
    
    db_queue.soft_delete()
    await db.commit()
    return True

