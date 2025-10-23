from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class Enterprise(AbstractBaseModel):
    __tablename__ = "enterprises"

    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    divisions = relationship("Division", back_populates="enterprise", cascade="all, delete-orphan")
    audit_plans = relationship("AuditPlan", back_populates="enterprise")
    audits = relationship("Audit", back_populates="enterprise")
    findings = relationship("Finding", back_populates="enterprise")

