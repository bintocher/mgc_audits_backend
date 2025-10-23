from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class SystemSetting(AbstractBaseModel):
    __tablename__ = "system_settings"

    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    is_encrypted = Column(Boolean, default=False, nullable=False)
    
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    updated_by = relationship("User", foreign_keys=[updated_by_id])

