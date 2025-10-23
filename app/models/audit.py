from sqlalchemy import Column, String, Date, Integer, ForeignKey, Text, Table, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


audit_locations = Table(
    "audit_locations",
    AbstractBaseModel.metadata,
    Column("audit_id", UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), primary_key=True),
    Column("location_id", UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True),
)

audit_clients = Table(
    "audit_clients",
    AbstractBaseModel.metadata,
    Column("audit_id", UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), primary_key=True),
    Column("client_id", UUID(as_uuid=True), ForeignKey("dictionaries.id", ondelete="CASCADE"), primary_key=True),
)

audit_shifts = Table(
    "audit_shifts",
    AbstractBaseModel.metadata,
    Column("audit_id", UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), primary_key=True),
    Column("shift_id", UUID(as_uuid=True), ForeignKey("dictionaries.id", ondelete="CASCADE"), primary_key=True),
)


class Audit(AbstractBaseModel):
    __tablename__ = "audits"

    title = Column(String(500), nullable=False)
    audit_number = Column(String(100), unique=True, nullable=False)
    subject = Column(String(500), nullable=False)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=False)
    audit_type_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=False)
    process_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=True)
    norm_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=True)
    status_id = Column(UUID(as_uuid=True), ForeignKey("statuses.id"), nullable=False)
    auditor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    responsible_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    audit_plan_item_id = Column(UUID(as_uuid=True), ForeignKey("audit_plan_items.id"), nullable=True)
    audit_date_from = Column(Date, nullable=False)
    audit_date_to = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)

    audit_category = Column(String(50), nullable=False)

    audit_result = Column(String(20), nullable=True)
    estimated_hours = Column(Numeric(10, 2), nullable=True)
    actual_hours = Column(Numeric(10, 2), nullable=True)

    risk_level_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=True)
    milestone_codes = Column(String(100), nullable=True)
    result_comment = Column(Text, nullable=True)
    manual_result_value = Column(String(50), nullable=True)

    pcd_planned_close_date = Column(Date, nullable=True)
    pcd_actual_close_date = Column(Date, nullable=True)
    pcd_status = Column(String(50), nullable=True)

    postponed_reason = Column(Text, nullable=True)
    rescheduled_date = Column(Date, nullable=True)
    rescheduled_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rescheduled_at = Column(DateTime(timezone=True), nullable=True)

    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_date = Column(Date, nullable=True)

    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    enterprise = relationship("Enterprise", foreign_keys=[enterprise_id])
    audit_type = relationship("Dictionary", foreign_keys=[audit_type_id])
    process = relationship("Dictionary", foreign_keys=[process_id])
    product = relationship("Dictionary", foreign_keys=[product_id])
    project = relationship("Dictionary", foreign_keys=[project_id])
    norm = relationship("Dictionary", foreign_keys=[norm_id])
    status = relationship("Status", foreign_keys=[status_id])
    auditor = relationship("User", foreign_keys=[auditor_id])
    responsible_user = relationship("User", foreign_keys=[responsible_user_id])
    audit_plan_item = relationship("AuditPlanItem", foreign_keys=[audit_plan_item_id])
    rescheduled_by = relationship("User", foreign_keys=[rescheduled_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])
    creator = relationship("User", foreign_keys=[created_by_id])
    risk_level = relationship("Dictionary", foreign_keys=[risk_level_id])

    locations = relationship("Location", secondary=audit_locations, back_populates="audits")
    clients = relationship("Dictionary", secondary=audit_clients)
    shifts = relationship("Dictionary", secondary=audit_shifts)

    components = relationship("AuditComponent", back_populates="audit", cascade="all, delete-orphan")
    schedule_weeks = relationship("AuditScheduleWeek", back_populates="audit", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="audit", cascade="all, delete-orphan")

