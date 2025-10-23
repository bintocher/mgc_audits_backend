from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.models.email_account import EmailAccount
from app.crud.email_account import get_email_credentials


async def send_email(
    account: EmailAccount,
    recipients: list[str],
    subject: str,
    body: str
):
    """
    Отправка email через указанный аккаунт.
    
    Args:
        account: Email аккаунт для отправки
        recipients: Список получателей
        subject: Тема письма
        body: Текст письма
    """
    credentials = get_email_credentials(account)
    
    config = ConnectionConfig(
        MAIL_USERNAME=account.smtp_user,
        MAIL_PASSWORD=credentials['smtp_password'],
        MAIL_FROM=account.from_email,
        MAIL_PORT=account.smtp_port,
        MAIL_SERVER=account.smtp_host,
        MAIL_FROM_NAME=account.from_name,
        MAIL_STARTTLS=account.use_tls,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )
    
    fast_mail = FastMail(config)
    
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype="plain"
    )
    
    await fast_mail.send_message(message)


async def send_registration_invite(
    account: EmailAccount,
    email: str,
    token: str,
    registration_url: str
):
    """
    Отправка email с приглашением на регистрацию.
    
    Args:
        account: Email аккаунт для отправки
        email: Email получателя
        token: Токен приглашения
        registration_url: URL для регистрации
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
    
    await send_email(account, [email], subject, body)


async def send_otp(
    account: EmailAccount,
    email: str,
    otp_code: str
):
    """
    Отправка OTP кода на email.
    
    Args:
        account: Email аккаунт для отправки
        email: Email получателя
        otp_code: OTP код
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
    
    await send_email(account, [email], subject, body)

