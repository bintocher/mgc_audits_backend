from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AttachmentBase(BaseModel):
    object_id: UUID
    content_type: str = Field(..., max_length=100)
    original_file_name: str = Field(..., max_length=255)
    s3_bucket: str = Field(..., max_length=100)
    s3_key: str = Field(..., max_length=500)
    file_size: int = Field(..., ge=0)
    mimetype: str = Field(..., max_length=100)


class AttachmentCreate(AttachmentBase):
    uploaded_by_id: UUID


class AttachmentUpdate(BaseModel):
    original_file_name: Optional[str] = Field(None, max_length=255)
    s3_bucket: Optional[str] = Field(None, max_length=100)
    s3_key: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = Field(None, ge=0)
    mimetype: Optional[str] = Field(None, max_length=100)


class AttachmentResponse(AttachmentBase):
    id: UUID
    uploaded_by_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    uploaded_by: Optional[dict] = None

    class Config:
        from_attributes = True

