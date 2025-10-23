from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=150)
    first_name_ru: str = Field(..., max_length=150)
    last_name_ru: str = Field(..., max_length=150)
    patronymic_ru: Optional[str] = Field(None, max_length=150)
    first_name_en: str = Field(..., max_length=150)
    last_name_en: str = Field(..., max_length=150)
    location_id: Optional[UUID] = None
    language: str = Field(default="ru", max_length=5)
    is_auditor: bool = False
    is_expert: bool = False
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=150)
    first_name_ru: Optional[str] = Field(None, max_length=150)
    last_name_ru: Optional[str] = Field(None, max_length=150)
    patronymic_ru: Optional[str] = Field(None, max_length=150)
    first_name_en: Optional[str] = Field(None, max_length=150)
    last_name_en: Optional[str] = Field(None, max_length=150)
    location_id: Optional[UUID] = None
    language: Optional[str] = Field(None, max_length=5)
    is_auditor: Optional[bool] = None
    is_expert: Optional[bool] = None
    is_active: Optional[bool] = None
    is_staff: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    id: UUID
    is_ldap_user: bool
    ldap_dn: Optional[str] = None
    telegram_chat_id: Optional[int] = None
    telegram_linked_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    pass


class UserMeResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    first_name_ru: str
    last_name_ru: str
    patronymic_ru: Optional[str]
    first_name_en: str
    last_name_en: str
    location_id: Optional[UUID]
    language: str
    is_auditor: bool
    is_expert: bool
    is_active: bool
    is_staff: bool
    is_superuser: bool
    telegram_linked: bool
    telegram_chat_id: Optional[int] = None

    class Config:
        from_attributes = True

