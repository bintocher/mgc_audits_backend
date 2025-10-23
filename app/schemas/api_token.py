from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class APITokenBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    rate_limit_per_minute: int = Field(default=30, ge=1, le=1000)
    rate_limit_per_hour: int = Field(default=500, ge=1, le=10000)
    expires_at: Optional[datetime] = None
    allowed_ips: Optional[str] = None


class APITokenCreate(APITokenBase):
    user_id: Optional[UUID] = None
    permission_mode: str = Field(default="inherit", pattern="^(inherit|custom)$")
    custom_permissions: Optional[str] = None
    issued_for: str = Field(default="user", pattern="^(user|system)$")


class APITokenUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=1000)
    rate_limit_per_hour: Optional[int] = Field(None, ge=1, le=10000)
    expires_at: Optional[datetime] = None
    allowed_ips: Optional[str] = None
    is_active: Optional[bool] = None


class APITokenResponse(APITokenBase):
    id: UUID
    token_prefix: str
    user_id: Optional[UUID] = None
    permission_mode: str
    issued_for: str
    is_active: bool
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class APITokenCreateResponse(APITokenResponse):
    plain_token: str


class TelegramLinkRequest(BaseModel):
    telegram_chat_id: int


class TelegramLinkResponse(BaseModel):
    message: str
    telegram_chat_id: int

