from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class EnterpriseBase(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=50)
    description: Optional[str] = None
    is_active: bool = True


class EnterpriseCreate(EnterpriseBase):
    pass


class EnterpriseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class EnterpriseResponse(EnterpriseBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EnterpriseInDB(EnterpriseResponse):
    pass

