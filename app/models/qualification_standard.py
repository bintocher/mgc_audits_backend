from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class QualificationStandard(AbstractBaseModel):
    __tablename__ = "qualification_standards"

    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    chapters = relationship("StandardChapter", back_populates="standard", cascade="all, delete-orphan")
    auditor_qualifications = relationship("AuditorQualification", secondary="auditor_qualification_standards", back_populates="standards")


class StandardChapter(AbstractBaseModel):
    __tablename__ = "standard_chapters"

    standard_id = Column(UUID(as_uuid=True), ForeignKey("qualification_standards.id"), nullable=False)
    name = Column(String(500), nullable=False)
    code = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    standard = relationship("QualificationStandard", back_populates="chapters")

