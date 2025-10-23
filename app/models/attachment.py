from sqlalchemy import Column, String, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from app.core.base import AbstractBaseModel


class Attachment(AbstractBaseModel):
    __tablename__ = "attachments"

    object_id = Column(UUID(as_uuid=True), nullable=False)
    content_type = Column(String(100), nullable=False)
    
    original_file_name = Column(String(255), nullable=False)
    s3_bucket = Column(String(100), nullable=False)
    s3_key = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mimetype = Column(String(100), nullable=False)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

