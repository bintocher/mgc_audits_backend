from datetime import datetime, timedelta
from typing import Optional
import secrets
import redis.asyncio as redis
from app.core.config import settings


class OTPService:
    def __init__(self):
        self.redis_client = None
        self.otp_expire_minutes = 10
    
    async def get_redis(self):
        if self.redis_client is None:
            self.redis_client = await redis.from_url(settings.REDIS_URL)
        return self.redis_client
    
    async def generate_otp(self, email: str) -> str:
        """
        Генерация OTP кода для email.
        
        Args:
            email: Email пользователя
        
        Returns:
            OTP код (6 цифр)
        """
        otp_code = f"{secrets.randbelow(1000000):06d}"
        
        redis_client = await self.get_redis()
        
        await redis_client.setex(
            f"otp:{email}",
            self.otp_expire_minutes * 60,
            otp_code
        )
        
        return otp_code
    
    async def verify_otp(self, email: str, otp_code: str) -> bool:
        """
        Проверка OTP кода.
        
        Args:
            email: Email пользователя
            otp_code: OTP код для проверки
        
        Returns:
            True если код верный, False иначе
        """
        redis_client = await self.get_redis()
        
        stored_code = await redis_client.get(f"otp:{email}")
        
        if stored_code is None:
            return False
        
        stored_code = stored_code.decode('utf-8')
        
        if stored_code != otp_code:
            return False
        
        await redis_client.delete(f"otp:{email}")
        
        return True
    
    async def invalidate_otp(self, email: str):
        """
        Инвалидация OTP кода.
        
        Args:
            email: Email пользователя
        """
        redis_client = await self.get_redis()
        await redis_client.delete(f"otp:{email}")


otp_service = OTPService()

