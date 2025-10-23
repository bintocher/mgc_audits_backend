from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class Location(AbstractBaseModel):
    __tablename__ = "locations"

    division_id = Column(UUID(as_uuid=True), ForeignKey("divisions.id"), nullable=False)
    name = Column(String(255), nullable=False)
    short_name = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    division = relationship("Division", back_populates="locations")
    users = relationship("User", back_populates="location")
    audits = relationship("Audit", secondary="audit_locations", back_populates="locations")

