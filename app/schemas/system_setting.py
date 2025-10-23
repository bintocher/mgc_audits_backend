from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class SystemSettingBase(BaseModel):
    key: str = Field(..., max_length=100)
    value: str
    value_type: str = Field(..., max_length=20)
    description: Optional[str] = None
    category: str = Field(..., max_length=50)
    is_public: bool = False
    is_encrypted: bool = False


class SystemSettingCreate(SystemSettingBase):
    pass


class SystemSettingUpdate(BaseModel):
    value: Optional[str] = None
    value_type: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    is_public: Optional[bool] = None
    is_encrypted: Optional[bool] = None


class SystemSettingResponse(SystemSettingBase):
    id: UUID
    updated_by_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

