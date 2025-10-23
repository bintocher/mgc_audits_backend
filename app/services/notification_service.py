from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.models.notification_queue import NotificationQueue
from app.models.user import User
from app.crud import notification as crud_notification
from app.schemas.notification import NotificationCreate
from app.services.email import send_email
from app.services.telegram_bot import telegram_bot_service
from app.crud.email_account import get_email_account


async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    event_type: str,
    entity_type: str,
    entity_id: UUID,
    title: str,
    message: str,
    notification_config: Optional[Dict[str, Any]] = None
) -> Notification:
    """
    Создать уведомление.
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя-получателя
        event_type: Тип события
        entity_type: Тип сущности
        entity_id: ID сущности
        title: Заголовок уведомления
        message: Текст уведомления
        notification_config: Конфигурация уведомления
    
    Returns:
        Созданное уведомление
    """
    notification_create = NotificationCreate(
        user_id=user_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        title=title,
        message=message,
        notification_config=notification_config
    )
    
    notification = await crud_notification.create_notification(db=db, notification=notification_create)
    
    return notification


async def send_notification_email(
    db: AsyncSession,
    notification: Notification,
    user: User
) -> bool:
    """
    Отправить уведомление по email.
    
    Args:
        db: Сессия базы данных
        notification: Уведомление
        user: Пользователь-получатель
    
    Returns:
        True если отправлено успешно, False в противном случае
    """
    try:
        account = await get_email_account(db=db)
        if not account:
            notification.email_error = "Email аккаунт не настроен"
            await db.commit()
            return False
        
        await send_email(
            account=account,
            recipients=[user.email],
            subject=notification.title,
            body=notification.message
        )
        
        notification.sent_email = True
        notification.email_sent_at = datetime.now()
        notification.email_error = None
        await db.commit()
        
        return True
    except Exception as e:
        notification.email_error = str(e)
        await db.commit()
        return False


async def send_notification_telegram(
    db: AsyncSession,
    notification: Notification,
    user: User
) -> bool:
    """
    Отправить уведомление в Telegram.
    
    Args:
        db: Сессия базы данных
        notification: Уведомление
        user: Пользователь-получатель
    
    Returns:
        True если отправлено успешно, False в противном случае
    """
    if not user.telegram_chat_id:
        notification.telegram_error = "Telegram не привязан"
        await db.commit()
        return False
    
    try:
        success = await telegram_bot_service.send_message(
            chat_id=user.telegram_chat_id,
            message=f"{notification.title}\n\n{notification.message}"
        )
        
        if success:
            notification.sent_telegram = True
            notification.telegram_sent_at = datetime.now()
            notification.telegram_error = None
        else:
            notification.telegram_error = "Не удалось отправить сообщение"
        
        await db.commit()
        return success
    except Exception as e:
        notification.telegram_error = str(e)
        await db.commit()
        return False


async def notify_finding_created(
    db: AsyncSession,
    finding_id: UUID,
    resolver_id: UUID,
    title: str,
    description: str
) -> None:
    """
    Отправить уведомление при создании finding.
    
    Args:
        db: Сессия базы данных
        finding_id: ID finding
        resolver_id: ID исполнителя
        title: Заголовок finding
        description: Описание finding
    """
    notification = await create_notification(
        db=db,
        user_id=resolver_id,
        event_type="finding_created",
        entity_type="finding",
        entity_id=finding_id,
        title=f"Новое несоответствие: {title}",
        message=f"Вам назначено новое несоответствие:\n\n{description}"
    )
    
    stmt = select(User).where(User.id == resolver_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        await send_notification_email(db=db, notification=notification, user=user)
        await send_notification_telegram(db=db, notification=notification, user=user)


async def notify_status_changed(
    db: AsyncSession,
    entity_type: str,
    entity_id: UUID,
    user_id: UUID,
    old_status: str,
    new_status: str
) -> None:
    """
    Отправить уведомление при изменении статуса.
    
    Args:
        db: Сессия базы данных
        entity_type: Тип сущности
        entity_id: ID сущности
        user_id: ID пользователя-получателя
        old_status: Старый статус
        new_status: Новый статус
    """
    notification = await create_notification(
        db=db,
        user_id=user_id,
        event_type="status_changed",
        entity_type=entity_type,
        entity_id=entity_id,
        title=f"Изменен статус {entity_type}",
        message=f"Статус изменен с '{old_status}' на '{new_status}'"
    )
    
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        await send_notification_email(db=db, notification=notification, user=user)
        await send_notification_telegram(db=db, notification=notification, user=user)


async def notify_deadline_approaching(
    db: AsyncSession,
    finding_id: UUID,
    resolver_id: UUID,
    deadline: datetime,
    title: str
) -> None:
    """
    Отправить уведомление при приближении deadline.
    
    Args:
        db: Сессия базы данных
        finding_id: ID finding
        resolver_id: ID исполнителя
        deadline: Дедлайн
        title: Заголовок finding
    """
    notification = await create_notification(
        db=db,
        user_id=resolver_id,
        event_type="deadline_approaching",
        entity_type="finding",
        entity_id=finding_id,
        title=f"Приближается дедлайн: {title}",
        message=f"Дедлайн для несоответствия '{title}' наступает {deadline.strftime('%d.%m.%Y')}"
    )
    
    stmt = select(User).where(User.id == resolver_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        await send_notification_email(db=db, notification=notification, user=user)
        await send_notification_telegram(db=db, notification=notification, user=user)


async def notify_deadline_overdue(
    db: AsyncSession,
    finding_id: UUID,
    resolver_id: UUID,
    deadline: datetime,
    title: str
) -> None:
    """
    Отправить уведомление при просрочке deadline.
    
    Args:
        db: Сессия базы данных
        finding_id: ID finding
        resolver_id: ID исполнителя
        deadline: Дедлайн
        title: Заголовок finding
    """
    notification = await create_notification(
        db=db,
        user_id=resolver_id,
        event_type="deadline_overdue",
        entity_type="finding",
        entity_id=finding_id,
        title=f"Просрочен дедлайн: {title}",
        message=f"Дедлайн для несоответствия '{title}' был {deadline.strftime('%d.%m.%Y')}"
    )
    
    stmt = select(User).where(User.id == resolver_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        await send_notification_email(db=db, notification=notification, user=user)
        await send_notification_telegram(db=db, notification=notification, user=user)


async def notify_delegation(
    db: AsyncSession,
    finding_id: UUID,
    from_user_id: UUID,
    to_user_id: UUID,
    title: str,
    reason: str
) -> None:
    """
    Отправить уведомление при делегировании.
    
    Args:
        db: Сессия базы данных
        finding_id: ID finding
        from_user_id: ID пользователя, от которого делегировано
        to_user_id: ID пользователя, которому делегировано
        title: Заголовок finding
        reason: Причина делегирования
    """
    notification = await create_notification(
        db=db,
        user_id=to_user_id,
        event_type="delegation",
        entity_type="finding",
        entity_id=finding_id,
        title=f"Делегировано несоответствие: {title}",
        message=f"Вам делегировано несоответствие '{title}'\n\nПричина: {reason}"
    )
    
    stmt = select(User).where(User.id == to_user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        await send_notification_email(db=db, notification=notification, user=user)
        await send_notification_telegram(db=db, notification=notification, user=user)


async def notify_comment_added(
    db: AsyncSession,
    finding_id: UUID,
    commenter_id: UUID,
    recipient_id: UUID,
    title: str,
    comment_text: str
) -> None:
    """
    Отправить уведомление при добавлении комментария.
    
    Args:
        db: Сессия базы данных
        finding_id: ID finding
        commenter_id: ID пользователя, который добавил комментарий
        recipient_id: ID пользователя-получателя
        title: Заголовок finding
        comment_text: Текст комментария
    """
    stmt_commenter = select(User).where(User.id == commenter_id)
    result_commenter = await db.execute(stmt_commenter)
    commenter = result_commenter.scalar_one_or_none()
    
    commenter_name = commenter.username if commenter else "Пользователь"
    
    notification = await create_notification(
        db=db,
        user_id=recipient_id,
        event_type="comment_added",
        entity_type="finding",
        entity_id=finding_id,
        title=f"Добавлен комментарий к: {title}",
        message=f"{commenter_name} добавил комментарий к несоответствию '{title}':\n\n{comment_text}"
    )
    
    stmt = select(User).where(User.id == recipient_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        await send_notification_email(db=db, notification=notification, user=user)
        await send_notification_telegram(db=db, notification=notification, user=user)

