from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    user_id: UUID
    event_type: str = Field(..., max_length=100)
    entity_type: str = Field(..., max_length=50)
    entity_id: UUID
    title: str = Field(..., max_length=500)
    message: str


class NotificationCreate(NotificationBase):
    notification_config: Optional[Dict[str, Any]] = None


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    sent_email: Optional[bool] = None
    sent_telegram: Optional[bool] = None
    email_sent_at: Optional[datetime] = None
    telegram_sent_at: Optional[datetime] = None
    email_error: Optional[str] = None
    telegram_error: Optional[str] = None
    retry_count: Optional[int] = None
    last_retry_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    id: UUID
    is_read: bool
    sent_email: bool
    sent_telegram: bool
    email_sent_at: Optional[datetime] = None
    telegram_sent_at: Optional[datetime] = None
    email_error: Optional[str] = None
    telegram_error: Optional[str] = None
    retry_count: int
    last_retry_at: Optional[datetime] = None
    notification_config: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    user: Optional[dict] = None

    class Config:
        from_attributes = True


class NotificationQueueBase(BaseModel):
    notification_id: UUID
    channel: str = Field(..., pattern="^(email|telegram)$")
    status: str = Field(..., pattern="^(pending|processing|sent|failed)$")
    priority: int = Field(default=0)
    scheduled_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)


class NotificationQueueCreate(NotificationQueueBase):
    pass


class NotificationQueueUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|processing|sent|failed)$")
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None


class NotificationQueueResponse(NotificationQueueBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    notification: Optional[dict] = None

    class Config:
        from_attributes = True


class NotificationStatsResponse(BaseModel):
    total_notifications: int
    unread_notifications: int
    email_sent: int
    telegram_sent: int
    failed_email: int
    failed_telegram: int
    by_event_type: Dict[str, int]
    by_channel: Dict[str, int]


class NotificationQueueStatsResponse(BaseModel):
    pending: int
    processing: int
    failed: int
    lag_minutes: Optional[float] = None
    size: int
    speed_per_minute: Optional[float] = None

