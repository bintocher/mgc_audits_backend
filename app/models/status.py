from sqlalchemy import Column, String, Boolean, Integer
from app.core.base import AbstractBaseModel


class Status(AbstractBaseModel):
    __tablename__ = "statuses"

    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, index=True)
    color = Column(String(7), nullable=False)
    entity_type = Column(String(50), nullable=False, index=True)
    order = Column(Integer, nullable=False)
    is_initial = Column(Boolean, default=False, nullable=False)
    is_final = Column(Boolean, default=False, nullable=False)

