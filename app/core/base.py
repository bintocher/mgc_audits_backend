from datetime import datetime, timezone
from typing import Any
from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declared_attr
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SoftDeleteMixin:
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class AbstractBaseModel(Base, TimestampMixin, SoftDeleteMixin):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

