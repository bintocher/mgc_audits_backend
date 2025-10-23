from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class LdapConnectionBase(BaseModel):
    name: str = Field(..., max_length=100)
    server_uri: str = Field(..., max_length=255)
    bind_dn: str = Field(..., max_length=255)
    bind_password: str = Field(..., max_length=500)
    user_search_base: str = Field(..., max_length=255)
    enterprise_id: Optional[UUID] = None
    division_id: Optional[UUID] = None
    is_default: bool = False
    is_active: bool = True


class LdapConnectionCreate(LdapConnectionBase):
    pass


class LdapConnectionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    server_uri: Optional[str] = Field(None, max_length=255)
    bind_dn: Optional[str] = Field(None, max_length=255)
    bind_password: Optional[str] = Field(None, max_length=500)
    user_search_base: Optional[str] = Field(None, max_length=255)
    enterprise_id: Optional[UUID] = None
    division_id: Optional[UUID] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class LdapConnectionResponse(LdapConnectionBase):
    id: UUID
    health_status: str
    last_checked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LdapConnectionTestResponse(BaseModel):
    success: bool
    message: str
    details: Optional[dict] = None

