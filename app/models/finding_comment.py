from sqlalchemy import Column, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base import AbstractBaseModel


class FindingComment(AbstractBaseModel):
    __tablename__ = "finding_comments"

    finding_id = Column(UUID(as_uuid=True), ForeignKey("findings.id"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)

    finding = relationship("Finding", back_populates="comments")
    author = relationship("User", foreign_keys=[author_id])

