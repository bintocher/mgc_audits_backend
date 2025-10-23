from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class AuditScheduleWeek(AbstractBaseModel):
    __tablename__ = "audit_schedule_weeks"

    audit_id = Column(UUID(as_uuid=True), ForeignKey("audits.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    manual_data = Column(String(100), nullable=True)
    calculated_result = Column(String(50), nullable=True)
    calculated_status = Column(String(50), nullable=True)
    color_override = Column(String(7), nullable=True)

    audit = relationship("Audit", back_populates="schedule_weeks")

