from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class Division(AbstractBaseModel):
    __tablename__ = "divisions"

    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=False)
    name = Column(String(255), nullable=False)
    short_name = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    enterprise = relationship("Enterprise", back_populates="divisions")
    locations = relationship("Location", back_populates="division", cascade="all, delete-orphan")

