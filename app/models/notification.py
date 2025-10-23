from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class Notification(AbstractBaseModel):
    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    sent_email = Column(Boolean, default=False, nullable=False)
    sent_telegram = Column(Boolean, default=False, nullable=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    telegram_sent_at = Column(DateTime(timezone=True), nullable=True)
    email_error = Column(Text, nullable=True)
    telegram_error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    last_retry_at = Column(DateTime(timezone=True), nullable=True)
    notification_config = Column(JSONB, nullable=True)

    user = relationship("User")
    queues = relationship("NotificationQueue", back_populates="notification", cascade="all, delete-orphan")

