from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.crud import s3_storage as crud_s3, email_account as crud_email, ldap_connection as crud_ldap
from app.schemas.s3_storage import S3StorageCreate, S3StorageUpdate, S3StorageResponse, S3StorageTestResponse
from app.schemas.email_account import EmailAccountCreate, EmailAccountUpdate, EmailAccountResponse, EmailAccountTestResponse
from app.schemas.ldap_connection import LdapConnectionCreate, LdapConnectionUpdate, LdapConnectionResponse, LdapConnectionTestResponse
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services import s3 as s3_service
from app.services import ldap as ldap_service


router = APIRouter(prefix="/integrations", tags=["integrations"])


# S3 Storages routes

@router.get("/s3_storages", response_model=List[S3StorageResponse])
async def get_s3_storages(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    enterprise_id: Optional[UUID] = None,
    division_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список S3 хранилищ с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        enterprise_id: Фильтр по ID предприятия
        division_id: Фильтр по ID дивизиона
        is_active: Фильтр по статусу активности
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Список S3 хранилищ
    """
    storages = await crud_s3.get_s3_storages(
        db=db,
        skip=skip,
        limit=limit,
        enterprise_id=enterprise_id,
        division_id=division_id,
        is_active=is_active
    )
    return storages


@router.get("/s3_storages/{id}", response_model=S3StorageResponse)
async def get_s3_storage(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить S3 хранилище по ID.
    
    Args:
        id: ID хранилища
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        S3 хранилище
    """
    storage = await crud_s3.get_s3_storage(db=db, storage_id=id)
    if not storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S3 storage not found"
        )
    return storage


@router.post("/s3_storages", response_model=S3StorageResponse, status_code=status.HTTP_201_CREATED)
async def create_s3_storage(
    storage: S3StorageCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новое S3 хранилище.
    
    Args:
        storage: Данные для создания хранилища
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Созданное S3 хранилище
    """
    new_storage = await crud_s3.create_s3_storage(db=db, storage=storage)
    return new_storage


@router.put("/s3_storages/{id}", response_model=S3StorageResponse)
async def update_s3_storage(
    id: UUID,
    storage_update: S3StorageUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить S3 хранилище.
    
    Args:
        id: ID хранилища
        storage_update: Данные для обновления
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Обновленное S3 хранилище
    """
    storage = await crud_s3.get_s3_storage(db=db, storage_id=id)
    if not storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S3 storage not found"
        )
    
    updated_storage = await crud_s3.update_s3_storage(
        db=db,
        storage_id=id,
        storage_update=storage_update
    )
    return updated_storage


@router.delete("/s3_storages/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_s3_storage(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить S3 хранилище (мягкое удаление).
    
    Args:
        id: ID хранилища
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    """
    success = await crud_s3.delete_s3_storage(db=db, storage_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S3 storage not found"
        )


@router.post("/s3_storages/{id}/test", response_model=S3StorageTestResponse)
async def test_s3_storage(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Проверить подключение к S3 хранилищу.
    
    Args:
        id: ID хранилища
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Результат проверки подключения
    """
    result = await s3_service.test_s3_connection(db=db, storage_id=id)
    return S3StorageTestResponse(**result)


# Email Accounts routes

@router.get("/email_accounts", response_model=List[EmailAccountResponse])
async def get_email_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    enterprise_id: Optional[UUID] = None,
    division_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список email аккаунтов с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        enterprise_id: Фильтр по ID предприятия
        division_id: Фильтр по ID дивизиона
        is_active: Фильтр по статусу активности
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Список email аккаунтов
    """
    accounts = await crud_email.get_email_accounts(
        db=db,
        skip=skip,
        limit=limit,
        enterprise_id=enterprise_id,
        division_id=division_id,
        is_active=is_active
    )
    return accounts


@router.get("/email_accounts/{id}", response_model=EmailAccountResponse)
async def get_email_account(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить email аккаунт по ID.
    
    Args:
        id: ID аккаунта
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Email аккаунт
    """
    account = await crud_email.get_email_account(db=db, account_id=id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    return account


@router.post("/email_accounts", response_model=EmailAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_email_account(
    account: EmailAccountCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новый email аккаунт.
    
    Args:
        account: Данные для создания аккаунта
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Созданный email аккаунт
    """
    new_account = await crud_email.create_email_account(db=db, account=account)
    return new_account


@router.put("/email_accounts/{id}", response_model=EmailAccountResponse)
async def update_email_account(
    id: UUID,
    account_update: EmailAccountUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить email аккаунт.
    
    Args:
        id: ID аккаунта
        account_update: Данные для обновления
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Обновленный email аккаунт
    """
    account = await crud_email.get_email_account(db=db, account_id=id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    updated_account = await crud_email.update_email_account(
        db=db,
        account_id=id,
        account_update=account_update
    )
    return updated_account


@router.delete("/email_accounts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_account(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить email аккаунт (мягкое удаление).
    
    Args:
        id: ID аккаунта
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    """
    success = await crud_email.delete_email_account(db=db, account_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )


@router.post("/email_accounts/{id}/test", response_model=EmailAccountTestResponse)
async def test_email_account(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Проверить подключение SMTP.
    
    Args:
        id: ID аккаунта
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Результат проверки подключения
    """
    account = await crud_email.get_email_account(db=db, account_id=id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    result = await ldap_service.test_email_connection(db=db, account_id=id)
    return EmailAccountTestResponse(**result)


# LDAP Connections routes

@router.get("/ldap_connections", response_model=List[LdapConnectionResponse])
async def get_ldap_connections(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    enterprise_id: Optional[UUID] = None,
    division_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список LDAP подключений с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        enterprise_id: Фильтр по ID предприятия
        division_id: Фильтр по ID дивизиона
        is_active: Фильтр по статусу активности
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Список LDAP подключений
    """
    connections = await crud_ldap.get_ldap_connections(
        db=db,
        skip=skip,
        limit=limit,
        enterprise_id=enterprise_id,
        division_id=division_id,
        is_active=is_active
    )
    return connections


@router.get("/ldap_connections/{id}", response_model=LdapConnectionResponse)
async def get_ldap_connection(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить LDAP подключение по ID.
    
    Args:
        id: ID подключения
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        LDAP подключение
    """
    connection = await crud_ldap.get_ldap_connection(db=db, connection_id=id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LDAP connection not found"
        )
    return connection


@router.post("/ldap_connections", response_model=LdapConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_ldap_connection(
    connection: LdapConnectionCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новое LDAP подключение.
    
    Args:
        connection: Данные для создания подключения
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Созданное LDAP подключение
    """
    new_connection = await crud_ldap.create_ldap_connection(db=db, connection=connection)
    return new_connection


@router.put("/ldap_connections/{id}", response_model=LdapConnectionResponse)
async def update_ldap_connection(
    id: UUID,
    connection_update: LdapConnectionUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить LDAP подключение.
    
    Args:
        id: ID подключения
        connection_update: Данные для обновления
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Обновленное LDAP подключение
    """
    connection = await crud_ldap.get_ldap_connection(db=db, connection_id=id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LDAP connection not found"
        )
    
    updated_connection = await crud_ldap.update_ldap_connection(
        db=db,
        connection_id=id,
        connection_update=connection_update
    )
    return updated_connection


@router.delete("/ldap_connections/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ldap_connection(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить LDAP подключение (мягкое удаление).
    
    Args:
        id: ID подключения
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    """
    success = await crud_ldap.delete_ldap_connection(db=db, connection_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LDAP connection not found"
        )


@router.post("/ldap_connections/{id}/test", response_model=LdapConnectionTestResponse)
async def test_ldap_connection(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Проверить подключение LDAP.
    
    Args:
        id: ID подключения
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Результат проверки подключения
    """
    connection = await crud_ldap.get_ldap_connection(db=db, connection_id=id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LDAP connection not found"
        )
    
    result = await ldap_service.test_ldap_connection(db=db, connection_id=id)
    return LdapConnectionTestResponse(**result)

