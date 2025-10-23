from sqlalchemy import Column, String, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class AuditPlanItem(AbstractBaseModel):
    __tablename__ = "audit_plan_items"

    audit_plan_id = Column(UUID(as_uuid=True), ForeignKey("audit_plans.id"), nullable=False)
    audit_type_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=False)
    process_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=True)
    norm_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=True)
    planned_auditor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    planned_date_from = Column(Date, nullable=False)
    planned_date_to = Column(Date, nullable=False)
    priority = Column(String(20), nullable=False, default='medium')  # 'high', 'medium', 'low'
    notes = Column(Text, nullable=True)

    # Relationships
    audit_plan = relationship("AuditPlan", back_populates="items")
    audit_type = relationship("Dictionary", foreign_keys=[audit_type_id])
    process = relationship("Dictionary", foreign_keys=[process_id])
    product = relationship("Dictionary", foreign_keys=[product_id])
    project = relationship("Dictionary", foreign_keys=[project_id])
    norm = relationship("Dictionary", foreign_keys=[norm_id])
    planned_auditor = relationship("User", foreign_keys=[planned_auditor_id])

