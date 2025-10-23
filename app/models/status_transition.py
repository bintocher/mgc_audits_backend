from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class StatusTransition(AbstractBaseModel):
    __tablename__ = "status_transitions"

    from_status_id = Column(UUID(as_uuid=True), ForeignKey("statuses.id"), nullable=False)
    to_status_id = Column(UUID(as_uuid=True), ForeignKey("statuses.id"), nullable=False)
    required_roles = Column(JSONB, nullable=True)
    required_fields = Column(JSONB, nullable=True)
    require_comment = Column(Boolean, default=False, nullable=False)
    notification_config = Column(JSONB, nullable=True)
    color = Column(String(7), nullable=True)

    from_status = relationship("Status", foreign_keys=[from_status_id])
    to_status = relationship("Status", foreign_keys=[to_status_id])

