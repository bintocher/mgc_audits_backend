from typing import List, Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings


class EmailService:
    def __init__(self):
        self.config = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.fast_mail = FastMail(self.config)
    
    async def send_registration_invite(
        self,
        email: str,
        token: str,
        registration_url: str
    ):
        """
        Отправка email с приглашением на регистрацию.
        """
        subject = "Приглашение на регистрацию"
        
        body = f"""
Здравствуйте!

Вы получили приглашение на регистрацию в системе аудитов.

Для завершения регистрации перейдите по ссылке:
{registration_url}?token={token}

Эта ссылка действительна в течение 72 часов.

Если вы не запрашивали это приглашение, просто проигнорируйте это письмо.

С уважением,
Команда MGC Audits
"""
        
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype="plain"
        )
        
        await self.fast_mail.send_message(message)
    
    async def send_otp(
        self,
        email: str,
        otp_code: str
    ):
        """
        Отправка OTP кода на email.
        """
        subject = "Код подтверждения MGC Audits"
        
        body = f"""
Здравствуйте!

Ваш код подтверждения для входа в систему MGC Audits:

{otp_code}

Код действителен в течение 10 минут.

Если вы не запрашивали этот код, проигнорируйте это письмо.

С уважением,
Команда MGC Audits
"""
        
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype="plain"
        )
        
        await self.fast_mail.send_message(message)


email_service = EmailService()

