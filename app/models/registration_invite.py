from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.base import AbstractBaseModel


class RegistrationInvite(AbstractBaseModel):
    __tablename__ = "registration_invites"

    email = Column(String(255), unique=True, nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_activated = Column(Boolean, default=False, nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    created_by = relationship("User", foreign_keys=[created_by_id])

