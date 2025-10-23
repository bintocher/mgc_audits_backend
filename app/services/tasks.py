from datetime import date, datetime
from typing import List
from app.core.celery_worker import celery_app
from app.core.database import async_session_maker
from app.models.auditor_qualification import AuditorQualification
from app.models.status import Status
from app.models.notification import Notification
from app.models.notification_queue import NotificationQueue
from app.models.user import User
from app.crud import notification as crud_notification
from app.services.notification_service import send_notification_email, send_notification_telegram
from sqlalchemy import select


@celery_app.task
def dummy_task():
    pass


@celery_app.task
async def check_expired_qualifications():
    """
    Проверяет квалификации аудиторов и меняет статус на expired для тех, у кого expiry_date прошла.
    Выполняется ежедневно через Celery Beat.
    """
    async with async_session_maker() as db:
        today = date.today()
        
        stmt = select(AuditorQualification).where(
            AuditorQualification.is_active == True,
            AuditorQualification.expiry_date < today
        )
        result = await db.execute(stmt)
        expired_qualifications = list(result.scalars().all())
        
        if not expired_qualifications:
            return {"updated": 0}
        
        expired_status_stmt = select(Status).where(Status.code == "expired")
        expired_status_result = await db.execute(expired_status_stmt)
        expired_status = expired_status_result.scalar_one_or_none()
        
        if not expired_status:
            return {"error": "Status 'expired' not found"}
        
        updated_count = 0
        for qualification in expired_qualifications:
            qualification.status_id = expired_status.id
            updated_count += 1
        
        await db.commit()
        
        return {"updated": updated_count}


@celery_app.task
async def send_email_notifications_batch():
    """
    Батчевая отправка email уведомлений из очереди.
    Выполняется каждую минуту через Celery Beat.
    """
    async with async_session_maker() as db:
        pending_queue = await crud_notification.get_pending_notifications(db=db, limit=50)
        
        if not pending_queue:
            return {"sent": 0, "failed": 0}
        
        sent_count = 0
        failed_count = 0
        
        for queue_item in pending_queue:
            if queue_item.channel != "email":
                continue
            
            notification = await crud_notification.get_notification(db=db, notification_id=queue_item.notification_id)
            if not notification:
                queue_item.status = "failed"
                queue_item.error_message = "Notification not found"
                failed_count += 1
                continue
            
            user_stmt = select(User).where(User.id == notification.user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                queue_item.status = "failed"
                queue_item.error_message = "User not found"
                failed_count += 1
                continue
            
            queue_item.status = "processing"
            await db.commit()
            
            success = await send_notification_email(db=db, notification=notification, user=user)
            
            if success:
                queue_item.status = "sent"
                queue_item.sent_at = datetime.now()
                sent_count += 1
            else:
                queue_item.status = "failed"
                queue_item.error_message = notification.email_error
                queue_item.retry_count += 1
                failed_count += 1
            
            await db.commit()
        
        return {"sent": sent_count, "failed": failed_count}


@celery_app.task
async def send_telegram_notifications_batch():
    """
    Батчевая отправка Telegram уведомлений из очереди.
    Выполняется каждую минуту через Celery Beat.
    """
    async with async_session_maker() as db:
        pending_queue = await crud_notification.get_pending_notifications(db=db, limit=50)
        
        if not pending_queue:
            return {"sent": 0, "failed": 0}
        
        sent_count = 0
        failed_count = 0
        
        for queue_item in pending_queue:
            if queue_item.channel != "telegram":
                continue
            
            notification = await crud_notification.get_notification(db=db, notification_id=queue_item.notification_id)
            if not notification:
                queue_item.status = "failed"
                queue_item.error_message = "Notification not found"
                failed_count += 1
                continue
            
            user_stmt = select(User).where(User.id == notification.user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                queue_item.status = "failed"
                queue_item.error_message = "User not found"
                failed_count += 1
                continue
            
            queue_item.status = "processing"
            await db.commit()
            
            success = await send_notification_telegram(db=db, notification=notification, user=user)
            
            if success:
                queue_item.status = "sent"
                queue_item.sent_at = datetime.now()
                sent_count += 1
            else:
                queue_item.status = "failed"
                queue_item.error_message = notification.telegram_error
                queue_item.retry_count += 1
                failed_count += 1
            
            await db.commit()
        
        return {"sent": sent_count, "failed": failed_count}


@celery_app.task
async def retry_failed_notifications():
    """
    Повторная отправка неудачных уведомлений с retry механизмом.
    Выполняется каждые 5 минут через Celery Beat.
    """
    async with async_session_maker() as db:
        failed_notifications = await crud_notification.get_notifications(
            db=db,
            skip=0,
            limit=100,
            user_id=None
        )
        
        retried_count = 0
        
        for notification in failed_notifications:
            if notification.retry_count >= 3:
                continue
            
            if notification.email_error and not notification.sent_email:
                user_stmt = select(User).where(User.id == notification.user_id)
                user_result = await db.execute(user_stmt)
                user = user_result.scalar_one_or_none()
                
                if user:
                    notification.retry_count += 1
                    notification.last_retry_at = datetime.now()
                    await db.commit()
                    
                    await send_notification_email(db=db, notification=notification, user=user)
                    retried_count += 1
            
            if notification.telegram_error and not notification.sent_telegram:
                user_stmt = select(User).where(User.id == notification.user_id)
                user_result = await db.execute(user_stmt)
                user = user_result.scalar_one_or_none()
                
                if user:
                    notification.retry_count += 1
                    notification.last_retry_at = datetime.now()
                    await db.commit()
                    
                    await send_notification_telegram(db=db, notification=notification, user=user)
                    retried_count += 1
        
        return {"retried": retried_count}

