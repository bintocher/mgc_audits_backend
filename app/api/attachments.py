from typing import List, Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.crud import attachment as crud_attachment
from app.crud.s3_storage import get_default_s3_storage, get_s3_storage
from app.schemas.attachment import AttachmentResponse
from app.services.s3 import upload_fileobj_to_s3, generate_presigned_url
from io import BytesIO
import os


router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.get("/", response_model=List[AttachmentResponse])
async def get_attachments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    object_id: Optional[UUID] = Query(None, description="Фильтр по ID объекта"),
    content_type: Optional[str] = Query(None, description="Фильтр по типу контента"),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список вложений с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        object_id: Фильтр по ID объекта
        content_type: Фильтр по типу контента
        db: Сессия базы данных
    
    Returns:
        Список вложений
    """
    attachments = await crud_attachment.get_attachments(
        db=db,
        skip=skip,
        limit=limit,
        object_id=object_id,
        content_type=content_type
    )
    return attachments


@router.post("/", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def create_attachment(
    file: UploadFile = File(...),
    object_id: UUID = Query(..., description="ID объекта"),
    content_type: str = Query(..., description="Тип контента (например, 'audit', 'finding')"),
    storage_id: Optional[UUID] = Query(None, description="ID S3 хранилища (если не указано, используется по умолчанию)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Загрузить вложение в систему и S3 хранилище.
    
    Args:
        file: Файл для загрузки
        object_id: ID объекта, к которому привязан файл
        content_type: Тип контента
        storage_id: ID S3 хранилища (опционально)
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Созданное вложение
    
    Raises:
        HTTPException: Если произошла ошибка при создании
    """
    from app.schemas.attachment import AttachmentCreate
    
    # Получаем S3 хранилище
    if storage_id:
        storage = await get_s3_storage(db, storage_id)
        if not storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="S3 storage not found"
            )
    else:
        storage = await get_default_s3_storage(db)
        if not storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No default S3 storage configured"
            )
    
    # Читаем содержимое файла
    file_contents = await file.read()
    file_size = len(file_contents)
    
    # Генерируем уникальный ключ для файла в S3
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"{uuid4()}{file_extension}"
    s3_key = f"{content_type}/{object_id}/{unique_filename}"
    
    # Загружаем файл в S3
    file_obj = BytesIO(file_contents)
    upload_success = upload_fileobj_to_s3(
        storage=storage,
        file_obj=file_obj,
        s3_key=s3_key,
        content_type=file.content_type or "application/octet-stream"
    )
    
    if not upload_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to S3"
        )
    
    # Создаем запись в БД
    attachment_data = AttachmentCreate(
        object_id=object_id,
        content_type=content_type,
        original_file_name=file.filename or "unnamed",
        s3_bucket=storage.bucket_name,
        s3_key=s3_key,
        file_size=file_size,
        mimetype=file.content_type or "application/octet-stream",
        uploaded_by_id=current_user.id
    )
    
    return await crud_attachment.create_attachment(db=db, attachment=attachment_data)


@router.get("/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(
    attachment_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию о вложении по ID.
    
    Args:
        attachment_id: UUID вложения
        db: Сессия базы данных
    
    Returns:
        Информация о вложении
    
    Raises:
        HTTPException: Если вложение не найдено
    """
    attachment = await crud_attachment.get_attachment(db, attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    return attachment


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Удалить вложение (мягкое удаление).
    
    Args:
        attachment_id: UUID вложения
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если вложение не найдено
    """
    success = await crud_attachment.delete_attachment(db, attachment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )


@router.get("/{attachment_id}/download_url")
async def get_attachment_download_url(
    attachment_id: UUID,
    expiration: int = Query(3600, ge=60, le=86400, description="Время действия URL в секундах (60-86400)"),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить pre-signed URL для скачивания вложения.
    
    Args:
        attachment_id: UUID вложения
        expiration: Время действия URL в секундах (по умолчанию 3600)
        db: Сессия базы данных
        current_user: Текущий пользователь
    
    Returns:
        Pre-signed URL для скачивания файла
    
    Raises:
        HTTPException: Если вложение не найдено или произошла ошибка при генерации URL
    """
    attachment = await crud_attachment.get_attachment(db, attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    # Находим S3 хранилище по bucket имени
    storage = await get_default_s3_storage(db)
    if not storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No default S3 storage configured"
        )
    
    # Генерируем pre-signed URL
    presigned_url = generate_presigned_url(
        storage=storage,
        s3_key=attachment.s3_key,
        expiration=expiration
    )
    
    if not presigned_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )
    
    return {
        "url": presigned_url,
        "expires_in": expiration,
        "filename": attachment.original_file_name
    }

