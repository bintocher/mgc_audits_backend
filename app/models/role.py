from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class Role(AbstractBaseModel):
    __tablename__ = "roles"

    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)

    permissions = relationship("Permission", back_populates="role", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class Permission(AbstractBaseModel):
    __tablename__ = "permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=True)
    resource = Column(String(100), nullable=False)
    action = Column(String(20), nullable=False)

    role = relationship("Role", back_populates="permissions")

