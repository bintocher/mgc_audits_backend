from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.export_task import ExportTaskStatus


class ExportTaskBase(BaseModel):
    audit_id: UUID
    status: ExportTaskStatus = ExportTaskStatus.PENDING


class ExportTaskCreate(ExportTaskBase):
    pass


class ExportTaskUpdate(BaseModel):
    status: Optional[ExportTaskStatus] = None
    celery_task_id: Optional[str] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class ExportTaskResponse(ExportTaskBase):
    id: UUID
    user_id: UUID
    celery_task_id: Optional[str] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ExportTaskStatusResponse(BaseModel):
    task_id: UUID
    celery_task_id: Optional[str] = None
    status: ExportTaskStatus
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None

