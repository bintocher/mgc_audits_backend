from sqlalchemy import Column, String, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class AuditComponent(AbstractBaseModel):
    __tablename__ = "audit_components"

    audit_id = Column(UUID(as_uuid=True), ForeignKey("audits.id"), nullable=False)
    component_type = Column(String(50), nullable=False)
    sap_id = Column(String(100), nullable=True)
    part_number = Column(String(100), nullable=True)
    component_name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    estimated_hours = Column(Numeric(10, 2), nullable=True)
    actual_hours = Column(Numeric(10, 2), nullable=True)

    audit = relationship("Audit", back_populates="components")

