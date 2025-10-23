from datetime import date
from app.core.celery_worker import celery_app
from app.core.database import async_session_maker
from app.models.auditor_qualification import AuditorQualification
from app.models.status import Status
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

