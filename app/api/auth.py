from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_password
)
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenPayload
)
from app.crud.registration_invite import create_invite, get_invite_by_email
from app.services.email import email_service
from app.services.ldap import ldap_service
from app.services.otp import otp_service
from app.schemas.auth import OTPSendRequest, OTPVerifyRequest
from pydantic import EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        session_id: str = payload.get("session_id")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user_id_uuid = UUID(user_id)
    
    result = await db.execute(select(User).where(User.id == user_id_uuid))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    if user.deleted_at is not None:
        raise credentials_exception
    
    if user.session_id != session_id:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход в систему через email и пароль.
    Возвращает access и refresh токены.
    """
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password not set"
        )
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
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


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление access токена по refresh токену.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    
    try:
        payload = decode_token(refresh_data.refresh_token)
        if payload is None:
            raise credentials_exception
        
        token_type: str = payload.get("type")
        if token_type != "refresh":
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        session_id: str = payload.get("session_id")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user_id_uuid = UUID(user_id)
    
    result = await db.execute(select(User).where(User.id == user_id_uuid))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    if user.deleted_at is not None:
        raise credentials_exception
    
    if user.session_id != session_id:
        raise credentials_exception
    
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


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Выход из системы. Инвалидирует текущую сессию.
    """
    current_user.session_id = None
    await db.commit()
    
    return {"message": "Successfully logged out"}


@router.post("/register")
async def register(
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация пользователя по токену-приглашению.
    """
    from app.models.registration_invite import RegistrationInvite
    
    result = await db.execute(
        select(RegistrationInvite).where(
            RegistrationInvite.token == register_data.token
        )
    )
    invite = result.scalar_one_or_none()
    
    if invite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid registration token"
        )
    
    if invite.is_activated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already used"
        )
    
    if invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired"
        )
    
    existing_user = await db.execute(
        select(User).where(User.email == invite.email)
    )
    if existing_user.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    password_hash = get_password_hash(register_data.password)
    
    new_user = User(
        email=invite.email,
        username=invite.email.split("@")[0],
        first_name_ru=register_data.first_name_ru,
        last_name_ru=register_data.last_name_ru,
        patronymic_ru=register_data.patronymic_ru,
        first_name_en=register_data.first_name_en,
        last_name_en=register_data.last_name_en,
        password_hash=password_hash,
        is_active=True,
        is_staff=False,
        is_superuser=False
    )
    
    db.add(new_user)
    
    invite.is_activated = True
    
    await db.commit()
    
    return {"message": "User registered successfully"}


@router.post("/invites/create")
async def create_registration_invite(
    email: EmailStr,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создание приглашения на регистрацию.
    Доступно только для администраторов.
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff users can create invites"
        )
    
    existing_invite = await get_invite_by_email(db, email)
    if existing_invite and not existing_invite.is_activated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite already exists for this email"
        )
    
    invite = await create_invite(db, email, current_user.id)
    
    registration_url = f"{settings.FRONTEND_URL}/register"
    
    try:
        await email_service.send_registration_invite(
            email=email,
            token=invite.token,
            registration_url=registration_url
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )
    
    return {
        "message": "Invite created and sent successfully",
        "invite_id": str(invite.id),
        "email": email
    }


@router.post("/ldap/login", response_model=LoginResponse)
async def ldap_login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход в систему через LDAP.
    Возвращает access и refresh токены.
    """
    ldap_user = await ldap_service.authenticate(login_data.email, login_data.password)
    
    if ldap_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid LDAP credentials"
        )
    
    result = await db.execute(
        select(User).where(User.email == ldap_user['email'])
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        password_hash = get_password_hash(generate_password())
        
        user = User(
            email=ldap_user['email'],
            username=ldap_user['username'],
            first_name_ru=ldap_user.get('first_name', ''),
            last_name_ru=ldap_user.get('last_name', ''),
            first_name_en=ldap_user.get('first_name', ''),
            last_name_en=ldap_user.get('last_name', ''),
            is_ldap_user=True,
            ldap_dn=ldap_user['dn'],
            password_hash=password_hash,
            is_active=True,
            is_staff=False,
            is_superuser=False
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
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

