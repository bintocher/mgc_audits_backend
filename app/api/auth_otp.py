from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token
from app.services.otp import otp_service
from app.services.email import send_otp
from app.crud.email_account import get_default_email_account
from app.schemas.auth import OTPSendRequest, OTPVerifyRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/generate")
async def generate_otp(
    request: OTPSendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Генерация OTP кода и отправка на email.
    """
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    otp_code = await otp_service.generate_otp(request.email)
    
    email_account = await get_default_email_account(db)
    if not email_account:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No email account configured"
        )
    
    try:
        await send_otp(
            account=email_account,
            email=request.email,
            otp_code=otp_code
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )
    
    return {"message": "OTP sent successfully"}


@router.post("/otp/verify", response_model=LoginResponse)
async def verify_otp(
    request: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Проверка OTP кода и возврат токенов.
    """
    is_valid = await otp_service.verify_otp(request.email, request.otp_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP code"
        )
    
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User deleted"
        )
    
    import secrets
    session_id = secrets.token_urlsafe(32)
    user.session_id = session_id
    user.last_login = datetime.now(timezone.utc)
    
    await db.commit()
    
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "session_id": session_id
        }
    )
    
    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "session_id": session_id
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

