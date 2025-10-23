from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class DictionaryType(AbstractBaseModel):
    __tablename__ = "dictionary_types"

    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(String, nullable=True)

    dictionaries = relationship("Dictionary", back_populates="dictionary_type", cascade="all, delete-orphan")


class Dictionary(AbstractBaseModel):
    __tablename__ = "dictionaries"

    dictionary_type_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_types.id"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    dictionary_type = relationship("DictionaryType", back_populates="dictionaries")
    enterprise = relationship("Enterprise")

