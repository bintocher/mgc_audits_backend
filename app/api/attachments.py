from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.crud import attachment as crud_attachment
from app.schemas.attachment import AttachmentResponse


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
    s3_bucket: str = Query(..., description="Имя S3 bucket"),
    s3_key: str = Query(..., description="S3 ключ"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Загрузить вложение в систему.
    
    Args:
        file: Файл для загрузки
        object_id: ID объекта, к которому привязан файл
        content_type: Тип контента
        s3_bucket: Имя S3 bucket
        s3_key: S3 ключ
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Созданное вложение
    
    Raises:
        HTTPException: Если произошла ошибка при создании
    """
    from app.schemas.attachment import AttachmentCreate
    
    file_contents = await file.read()
    file_size = len(file_contents)
    
    attachment_data = AttachmentCreate(
        object_id=object_id,
        content_type=content_type,
        original_file_name=file.filename,
        s3_bucket=s3_bucket,
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

