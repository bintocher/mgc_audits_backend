from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from datetime import datetime, timezone
from app.core.base import AbstractBaseModel


class ExportTaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportTask(AbstractBaseModel):
    __tablename__ = "export_tasks"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audit.id"), nullable=False)
    status = Column(Enum(ExportTaskStatus), default=ExportTaskStatus.PENDING, nullable=False)
    celery_task_id = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    error_message = Column(String(1000), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<ExportTask(id={self.id}, audit_id={self.audit_id}, status={self.status})>"

