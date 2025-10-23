from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.email_account import EmailAccount
from app.schemas.email_account import EmailAccountCreate, EmailAccountUpdate
from app.core.security import encrypt_value, decrypt_value


async def create_email_account(db: AsyncSession, account: EmailAccountCreate) -> EmailAccount:
    db_account = EmailAccount(
        name=account.name,
        from_name=account.from_name,
        from_email=account.from_email,
        smtp_host=account.smtp_host,
        smtp_port=account.smtp_port,
        smtp_user=account.smtp_user,
        smtp_password=encrypt_value(account.smtp_password),
        use_tls=account.use_tls,
        enterprise_id=account.enterprise_id,
        division_id=account.division_id,
        is_default=account.is_default,
        is_active=account.is_active
    )
    db.add(db_account)
    await db.commit()
    await db.refresh(db_account)
    return db_account


async def get_email_account(db: AsyncSession, account_id: UUID) -> Optional[EmailAccount]:
    stmt = select(EmailAccount).where(EmailAccount.id == account_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_email_accounts(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    enterprise_id: Optional[UUID] = None,
    division_id: Optional[UUID] = None,
    is_active: Optional[bool] = None
) -> List[EmailAccount]:
    stmt = select(EmailAccount)
    
    if enterprise_id is not None:
        stmt = stmt.where(EmailAccount.enterprise_id == enterprise_id)
    
    if division_id is not None:
        stmt = stmt.where(EmailAccount.division_id == division_id)
    
    if is_active is not None:
        stmt = stmt.where(EmailAccount.is_active == is_active)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_email_account(
    db: AsyncSession,
    account_id: UUID,
    account_update: EmailAccountUpdate
) -> Optional[EmailAccount]:
    db_account = await get_email_account(db, account_id)
    if not db_account:
        return None
    
    update_data = account_update.model_dump(exclude_unset=True)
    
    if "smtp_password" in update_data:
        update_data["smtp_password"] = encrypt_value(update_data["smtp_password"])
    
    for field, value in update_data.items():
        setattr(db_account, field, value)
    
    await db.commit()
    await db.refresh(db_account)
    return db_account


async def delete_email_account(db: AsyncSession, account_id: UUID) -> bool:
    db_account = await get_email_account(db, account_id)
    if not db_account:
        return False
    
    db_account.soft_delete()
    await db.commit()
    return True


async def get_default_email_account(db: AsyncSession) -> Optional[EmailAccount]:
    stmt = select(EmailAccount).where(EmailAccount.is_default == True, EmailAccount.is_active == True)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def get_email_credentials(db_account: EmailAccount) -> dict:
    return {
        "smtp_password": decrypt_value(db_account.smtp_password)
    }

