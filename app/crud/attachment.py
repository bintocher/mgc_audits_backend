from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentCreate, AttachmentUpdate


async def create_attachment(db: AsyncSession, attachment: AttachmentCreate) -> Attachment:
    db_attachment = Attachment(
        object_id=attachment.object_id,
        content_type=attachment.content_type,
        original_file_name=attachment.original_file_name,
        s3_bucket=attachment.s3_bucket,
        s3_key=attachment.s3_key,
        file_size=attachment.file_size,
        mimetype=attachment.mimetype,
        uploaded_by_id=attachment.uploaded_by_id
    )
    
    db.add(db_attachment)
    await db.commit()
    await db.refresh(db_attachment)
    return db_attachment


async def get_attachment(db: AsyncSession, attachment_id: UUID) -> Optional[Attachment]:
    stmt = select(Attachment).where(Attachment.id == attachment_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_attachments(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    object_id: Optional[UUID] = None,
    content_type: Optional[str] = None
) -> List[Attachment]:
    stmt = select(Attachment)
    
    if object_id is not None:
        stmt = stmt.where(Attachment.object_id == object_id)
    
    if content_type is not None:
        stmt = stmt.where(Attachment.content_type == content_type)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_attachment(
    db: AsyncSession,
    attachment_id: UUID,
    attachment_update: AttachmentUpdate
) -> Optional[Attachment]:
    db_attachment = await get_attachment(db, attachment_id)
    if not db_attachment:
        return None
    
    update_data = attachment_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_attachment, field, value)
    
    await db.commit()
    await db.refresh(db_attachment)
    return db_attachment


async def delete_attachment(db: AsyncSession, attachment_id: UUID) -> bool:
    db_attachment = await get_attachment(db, attachment_id)
    if not db_attachment:
        return False
    
    db_attachment.soft_delete()
    await db.commit()
    return True

