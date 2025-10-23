from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class S3Storage(AbstractBaseModel):
    __tablename__ = "s3_storages"

    name = Column(String(100), nullable=False)
    endpoint_url = Column(String(255), nullable=False)
    region = Column(String(50), nullable=False)
    access_key_id = Column(String(200), nullable=False)
    secret_access_key = Column(String(500), nullable=False)
    bucket_name = Column(String(100), nullable=False)
    prefix = Column(String(200), nullable=True)
    
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=True)
    division_id = Column(UUID(as_uuid=True), ForeignKey("divisions.id"), nullable=True)
    
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    health_status = Column(String(20), default="ok", nullable=False)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    enterprise = relationship("Enterprise", foreign_keys=[enterprise_id])
    division = relationship("Division", foreign_keys=[division_id])

