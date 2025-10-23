from sqlalchemy import Column, String, Boolean, BigInteger, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.base import AbstractBaseModel


class User(AbstractBaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(150), unique=True, nullable=False)
    
    first_name_ru = Column(String(150), nullable=False)
    last_name_ru = Column(String(150), nullable=False)
    patronymic_ru = Column(String(150), nullable=True)
    
    first_name_en = Column(String(150), nullable=False)
    last_name_en = Column(String(150), nullable=False)
    
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)
    
    is_ldap_user = Column(Boolean, default=False, nullable=False)
    ldap_dn = Column(String(255), nullable=True, index=True)
    
    language = Column(String(5), default="ru", nullable=False)
    
    telegram_chat_id = Column(BigInteger, nullable=True, index=True)
    telegram_linked_at = Column(DateTime(timezone=True), nullable=True)
    
    is_auditor = Column(Boolean, default=False, nullable=False)
    is_expert = Column(Boolean, default=False, nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_staff = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    password_hash = Column(String(255), nullable=True)
    session_id = Column(String(255), nullable=True)

    location = relationship("Location", back_populates="users")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

