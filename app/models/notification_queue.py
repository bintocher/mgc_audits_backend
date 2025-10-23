from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class NotificationQueue(AbstractBaseModel):
    __tablename__ = "notification_queue"

    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.id"), nullable=False, index=True)
    channel = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    priority = Column(Integer, default=0, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)

    notification = relationship("Notification", back_populates="queues")

