from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "mgc_audits",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.services.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule_filename="temp/celerybeat-schedule",
    beat_schedule={
        "check-expired-qualifications": {
            "task": "app.services.tasks.check_expired_qualifications",
            "schedule": 86400.0,
        },
        "send-email-notifications-batch": {
            "task": "app.services.tasks.send_email_notifications_batch",
            "schedule": 60.0,
        },
        "send-telegram-notifications-batch": {
            "task": "app.services.tasks.send_telegram_notifications_batch",
            "schedule": 60.0,
        },
        "retry-failed-notifications": {
            "task": "app.services.tasks.retry_failed_notifications",
            "schedule": 300.0,
        },
    },
)

if __name__ == "__main__":
    celery_app.start()

