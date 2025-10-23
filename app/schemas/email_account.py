from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class EmailAccountBase(BaseModel):
    name: str = Field(..., max_length=100)
    from_name: str = Field(..., max_length=100)
    from_email: str = Field(..., max_length=255)
    smtp_host: str = Field(..., max_length=255)
    smtp_port: int
    smtp_user: str = Field(..., max_length=255)
    smtp_password: str = Field(..., max_length=500)
    use_tls: bool = True
    enterprise_id: Optional[UUID] = None
    division_id: Optional[UUID] = None
    is_default: bool = False
    is_active: bool = True


class EmailAccountCreate(EmailAccountBase):
    pass


class EmailAccountUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    from_name: Optional[str] = Field(None, max_length=100)
    from_email: Optional[str] = Field(None, max_length=255)
    smtp_host: Optional[str] = Field(None, max_length=255)
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = Field(None, max_length=255)
    smtp_password: Optional[str] = Field(None, max_length=500)
    use_tls: Optional[bool] = None
    enterprise_id: Optional[UUID] = None
    division_id: Optional[UUID] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class EmailAccountResponse(EmailAccountBase):
    id: UUID
    health_status: str
    last_checked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmailAccountTestResponse(BaseModel):
    success: bool
    message: str
    details: Optional[dict] = None

