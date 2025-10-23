import logging
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.s3_storage import get_s3_storage, get_storage_credentials
from app.models.s3_storage import S3Storage


logger = logging.getLogger(__name__)


def get_s3_client(storage: S3Storage) -> boto3.client:
    credentials = get_storage_credentials(storage)
    
    config = Config(
        signature_version='s3v4',
        retries={'max_attempts': 3, 'mode': 'standard'}
    )
    
    client = boto3.client(
        's3',
        endpoint_url=storage.endpoint_url,
        region_name=storage.region,
        aws_access_key_id=credentials['access_key_id'],
        aws_secret_access_key=credentials['secret_access_key'],
        config=config
    )
    
    return client


async def test_s3_connection(db: AsyncSession, storage_id: UUID) -> dict:
    storage = await get_s3_storage(db, storage_id)
    if not storage:
        return {
            "success": False,
            "message": "S3 storage not found",
            "details": None
        }
    
    try:
        client = get_s3_client(storage)
        
        client.head_bucket(Bucket=storage.bucket_name)
        
        storage.health_status = "ok"
        storage.error_message = None
        
        from datetime import datetime, timezone
        storage.last_checked_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Connection successful",
            "details": {
                "bucket": storage.bucket_name,
                "region": storage.region,
                "endpoint": storage.endpoint_url
            }
        }
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = str(e)
        
        storage.health_status = "error"
        storage.error_message = error_message
        
        from datetime import datetime, timezone
        storage.last_checked_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        logger.error(f"S3 connection test failed: {error_message}")
        
        return {
            "success": False,
            "message": f"Connection failed: {error_code}",
            "details": {
                "error": error_message
            }
        }
    except Exception as e:
        error_message = str(e)
        
        storage.health_status = "error"
        storage.error_message = error_message
        
        from datetime import datetime, timezone
        storage.last_checked_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        logger.error(f"S3 connection test failed: {error_message}")
        
        return {
            "success": False,
            "message": f"Connection failed: {error_message}",
            "details": {
                "error": error_message
            }
        }


def upload_file_to_s3(storage: S3Storage, file_path: str, s3_key: str) -> bool:
    try:
        client = get_s3_client(storage)
        
        full_key = f"{storage.prefix}{s3_key}" if storage.prefix else s3_key
        
        client.upload_file(file_path, storage.bucket_name, full_key)
        
        return True
    except ClientError as e:
        logger.error(f"Failed to upload file to S3: {e}")
        return False


def upload_fileobj_to_s3(storage: S3Storage, file_obj, s3_key: str, content_type: Optional[str] = None) -> bool:
    """
    Загружает файл из файлового объекта в S3 бакет.
    
    Args:
        storage: S3 хранилище
        file_obj: Файловый объект (BytesIO, FileStorage и т.д.)
        s3_key: S3 ключ объекта
        content_type: MIME тип файла (опционально)
    
    Returns:
        True если загрузка успешна, False в противном случае
    """
    try:
        client = get_s3_client(storage)
        
        full_key = f"{storage.prefix}{s3_key}" if storage.prefix else s3_key
        
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        
        client.upload_fileobj(file_obj, storage.bucket_name, full_key, ExtraArgs=extra_args)
        
        return True
    except ClientError as e:
        logger.error(f"Failed to upload file to S3: {e}")
        return False


def generate_presigned_url(storage: S3Storage, s3_key: str, expiration: int = 3600) -> Optional[str]:
    try:
        client = get_s3_client(storage)
        
        full_key = f"{storage.prefix}{s3_key}" if storage.prefix else s3_key
        
        url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': storage.bucket_name, 'Key': full_key},
            ExpiresIn=expiration
        )
        
        return url
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        return None


def generate_presigned_post_url(storage: S3Storage, s3_key: str, expiration: int = 3600) -> Optional[dict]:
    try:
        client = get_s3_client(storage)
        
        full_key = f"{storage.prefix}{s3_key}" if storage.prefix else s3_key
        
        response = client.generate_presigned_post(
            storage.bucket_name,
            full_key,
            ExpiresIn=expiration
        )
        
        return response
    except ClientError as e:
        logger.error(f"Failed to generate presigned POST URL: {e}")
        return None


def delete_file_from_s3(storage: S3Storage, s3_key: str) -> bool:
    try:
        client = get_s3_client(storage)
        
        full_key = f"{storage.prefix}{s3_key}" if storage.prefix else s3_key
        
        client.delete_object(Bucket=storage.bucket_name, Key=full_key)
        
        return True
    except ClientError as e:
        logger.error(f"Failed to delete file from S3: {e}")
        return False
