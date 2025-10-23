from sqlalchemy import Column, String, ForeignKey, Text, Date, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class Finding(AbstractBaseModel):
    __tablename__ = "findings"

    finding_number = Column(Integer, unique=True, nullable=False, autoincrement=True)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audits.id"), nullable=False)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    process_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id"), nullable=False)
    status_id = Column(UUID(as_uuid=True), ForeignKey("statuses.id"), nullable=False)
    finding_type = Column(String(20), nullable=False)
    resolver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deadline = Column(Date, nullable=False)
    closing_date = Column(Date, nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    why_1 = Column(Text, nullable=True)
    why_2 = Column(Text, nullable=True)
    why_3 = Column(Text, nullable=True)
    why_4 = Column(Text, nullable=True)
    why_5 = Column(Text, nullable=True)

    immediate_action = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    long_term_action = Column(Text, nullable=True)
    action_verification = Column(Text, nullable=True)
    preventive_measures = Column(Text, nullable=True)

    audit = relationship("Audit", back_populates="findings")
    enterprise = relationship("Enterprise", foreign_keys=[enterprise_id])
    process = relationship("Dictionary", foreign_keys=[process_id])
    status = relationship("Status", foreign_keys=[status_id])
    resolver = relationship("User", foreign_keys=[resolver_id])
    approver = relationship("User", foreign_keys=[approver_id])
    creator = relationship("User", foreign_keys=[created_by_id])
    
    delegations = relationship("FindingDelegation", back_populates="finding", cascade="all, delete-orphan")
    comments = relationship("FindingComment", back_populates="finding", cascade="all, delete-orphan")

