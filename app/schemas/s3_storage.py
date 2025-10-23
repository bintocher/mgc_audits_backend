from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class S3StorageBase(BaseModel):
    name: str = Field(..., max_length=100)
    endpoint_url: str = Field(..., max_length=255)
    region: str = Field(..., max_length=50)
    access_key_id: str = Field(..., max_length=200)
    secret_access_key: str = Field(..., max_length=500)
    bucket_name: str = Field(..., max_length=100)
    prefix: Optional[str] = Field(None, max_length=200)
    enterprise_id: Optional[UUID] = None
    division_id: Optional[UUID] = None
    is_default: bool = False
    is_active: bool = True


class S3StorageCreate(S3StorageBase):
    pass


class S3StorageUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    endpoint_url: Optional[str] = Field(None, max_length=255)
    region: Optional[str] = Field(None, max_length=50)
    access_key_id: Optional[str] = Field(None, max_length=200)
    secret_access_key: Optional[str] = Field(None, max_length=500)
    bucket_name: Optional[str] = Field(None, max_length=100)
    prefix: Optional[str] = Field(None, max_length=200)
    enterprise_id: Optional[UUID] = None
    division_id: Optional[UUID] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class S3StorageResponse(S3StorageBase):
    id: UUID
    health_status: str
    last_checked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class S3StorageTestResponse(BaseModel):
    success: bool
    message: str
    details: Optional[dict] = None

