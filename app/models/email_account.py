from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class EmailAccount(AbstractBaseModel):
    __tablename__ = "email_accounts"

    name = Column(String(100), nullable=False)
    from_name = Column(String(100), nullable=False)
    from_email = Column(String(255), nullable=False)
    smtp_host = Column(String(255), nullable=False)
    smtp_port = Column(Integer, nullable=False)
    smtp_user = Column(String(255), nullable=False)
    smtp_password = Column(String(500), nullable=False)
    use_tls = Column(Boolean, default=True, nullable=False)
    
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=True)
    division_id = Column(UUID(as_uuid=True), ForeignKey("divisions.id"), nullable=True)
    
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    health_status = Column(String(20), default="ok", nullable=False)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    enterprise = relationship("Enterprise", foreign_keys=[enterprise_id])
    division = relationship("Division", foreign_keys=[division_id])

