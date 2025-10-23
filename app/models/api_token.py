from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.base import AbstractBaseModel


class APIToken(AbstractBaseModel):
    __tablename__ = "api_tokens"

    name = Column(String(255), nullable=False)
    token_prefix = Column(String(16), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    custom_permissions = Column(Text, nullable=True)
    rate_limit_per_minute = Column(Integer, default=30, nullable=False)
    rate_limit_per_hour = Column(Integer, default=500, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    issued_for = Column(String(10), nullable=False)
    permission_mode = Column(String(10), nullable=False)
    allowed_ips = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    user = relationship("User", foreign_keys=[user_id])

