from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    token: str
    first_name_ru: str
    last_name_ru: str
    patronymic_ru: Optional[str] = None
    first_name_en: str
    last_name_en: str
    password: str


class OTPSendRequest(BaseModel):
    email: EmailStr


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str


class TokenPayload(BaseModel):
    sub: UUID
    type: str
    session_id: Optional[str] = None

