from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.models.export_task import ExportTask, ExportTaskStatus
from app.schemas.export_task import ExportTaskCreate, ExportTaskUpdate


async def create_export_task(
    db: AsyncSession,
    export_task: ExportTaskCreate,
    user_id: UUID
) -> ExportTask:
    db_export_task = ExportTask(
        **export_task.model_dump(),
        user_id=user_id
    )
    db.add(db_export_task)
    await db.commit()
    await db.refresh(db_export_task)
    return db_export_task


async def get_export_task(
    db: AsyncSession,
    export_task_id: UUID
) -> Optional[ExportTask]:
    stmt = select(ExportTask).where(ExportTask.id == export_task_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_export_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[UUID] = None,
    audit_id: Optional[UUID] = None,
    status: Optional[ExportTaskStatus] = None
) -> List[ExportTask]:
    stmt = select(ExportTask)
    
    if user_id:
        stmt = stmt.where(ExportTask.user_id == user_id)
    if audit_id:
        stmt = stmt.where(ExportTask.audit_id == audit_id)
    if status:
        stmt = stmt.where(ExportTask.status == status)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_export_task(
    db: AsyncSession,
    export_task_id: UUID,
    export_task_update: ExportTaskUpdate
) -> Optional[ExportTask]:
    db_export_task = await get_export_task(db, export_task_id)
    if not db_export_task:
        return None
    
    update_data = export_task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_export_task, field, value)
    
    await db.commit()
    await db.refresh(db_export_task)
    return db_export_task


async def delete_export_task(
    db: AsyncSession,
    export_task_id: UUID
) -> bool:
    db_export_task = await get_export_task(db, export_task_id)
    if not db_export_task:
        return False
    
    db_export_task.soft_delete()
    await db.commit()
    return True


async def get_export_task_by_celery_id(
    db: AsyncSession,
    celery_task_id: str
) -> Optional[ExportTask]:
    stmt = select(ExportTask).where(ExportTask.celery_task_id == celery_task_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

