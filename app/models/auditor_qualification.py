from sqlalchemy import Column, String, Boolean, Date, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


auditor_qualification_standards = Table(
    "auditor_qualification_standards",
    AbstractBaseModel.metadata,
    Column("auditor_qualification_id", UUID(as_uuid=True), ForeignKey("auditor_qualifications.id", ondelete="CASCADE"), primary_key=True),
    Column("qualification_standard_id", UUID(as_uuid=True), ForeignKey("qualification_standards.id", ondelete="CASCADE"), primary_key=True),
)


class AuditorQualification(AbstractBaseModel):
    __tablename__ = "auditor_qualifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status_id = Column(UUID(as_uuid=True), ForeignKey("statuses.id"), nullable=False)
    certification_body = Column(String(255), nullable=False)
    certificate_number = Column(String(100), nullable=False)
    certificate_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    additional_info = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="auditor_qualifications")
    status = relationship("Status", foreign_keys=[status_id])
    standards = relationship("QualificationStandard", secondary=auditor_qualification_standards, back_populates="auditor_qualifications")

