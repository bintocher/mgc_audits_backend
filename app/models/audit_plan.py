from sqlalchemy import Column, String, Boolean, Integer, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class AuditPlan(AbstractBaseModel):
    __tablename__ = "audit_plans"

    title = Column(String(500), nullable=False)
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=False)
    category = Column(String(50), nullable=False)  # 'product', 'process_system', 'lra', 'external'
    status = Column(String(20), nullable=False, default='draft')  # 'draft', 'approved', 'in_progress', 'completed'
    version_number = Column(Integer, nullable=False, default=1)

    # Согласование на уровне Дивизиона
    approved_by_division = Column(Boolean, nullable=False, default=False)
    approved_by_division_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_by_division_at = Column(DateTime(timezone=True), nullable=True)

    # Согласование на уровне УК (управляющей компании)
    approved_by_uk = Column(Boolean, nullable=False, default=False)
    approved_by_uk_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_by_uk_at = Column(DateTime(timezone=True), nullable=True)

    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    enterprise = relationship("Enterprise", foreign_keys=[enterprise_id])
    division_approver = relationship("User", foreign_keys=[approved_by_division_user_id])
    uk_approver = relationship("User", foreign_keys=[approved_by_uk_user_id])
    creator = relationship("User", foreign_keys=[created_by_id])
    items = relationship("AuditPlanItem", back_populates="audit_plan", cascade="all, delete-orphan")

