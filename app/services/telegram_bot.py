from typing import Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.core.config import settings
import redis.asyncio as redis


class TelegramBotService:
    def __init__(self):
        self.token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        self.app = None
        self.redis_client = None
    
    async def get_redis(self):
        if self.redis_client is None:
            self.redis_client = await redis.from_url(settings.REDIS_URL)
        return self.redis_client
    
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик команды /start бота.
        """
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        message = f"""
Привет, {username}!

Это бот для интеграции с системой MGC Audits.

Для привязки аккаунта:
1. Перейдите в настройки профиля в системе
2. Нажмите "Привязать Telegram"
3. Отправьте полученный код боту

Для получения уведомлений включите их в настройках профиля.

Команды:
/start - показать это сообщение
/help - справка
/link <code> - привязать аккаунт (используйте код из системы)
"""
        
        await update.message.reply_text(message)
    
    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик команды /help бота.
        """
        message = """
Доступные команды:

/start - начать работу с ботом
/help - показать эту справку
/link <code> - привязать Telegram к аккаунту в системе

Для привязки:
1. Перейдите в настройки профиля в веб-интерфейсе
2. Нажмите "Привязать Telegram"
3. Отправьте полученный код боту командой /link <code>

После привязки вы будете получать уведомления в Telegram.
"""
        
        await update.message.reply_text(message)
    
    async def link_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик команды /link для привязки аккаунта.
        """
        if not context.args:
            await update.message.reply_text("Использование: /link <code>")
            return
        
        code = context.args[0]
        chat_id = update.effective_chat.id
        
        redis_client = await self.get_redis()
        
        email = await redis_client.get(f"telegram_link:{code}")
        
        if email is None:
            await update.message.reply_text("Неверный код привязки. Код мог истечь.")
            return
        
        email = email.decode('utf-8')
        
        await redis_client.set(f"telegram_linked:{email}", str(chat_id), ex=3600)
        await redis_client.delete(f"telegram_link:{code}")
        
        await update.message.reply_text(
            f"Аккаунт успешно привязан!\n"
            f"Email: {email}\n"
            f"Telegram ID: {chat_id}\n\n"
            f"Теперь завершите привязку в веб-интерфейсе."
        )
    
    async def initialize(self):
        """
        Инициализация бота и регистрация обработчиков.
        """
        if not self.token:
            print("TELEGRAM_BOT_TOKEN not set, skipping bot initialization")
            return
        
        self.app = Application.builder().token(self.token).build()
        
        self.app.add_handler(CommandHandler("start", self.start_handler))
        self.app.add_handler(CommandHandler("help", self.help_handler))
        self.app.add_handler(CommandHandler("link", self.link_handler))
        
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
    
    async def send_message(self, chat_id: int, message: str):
        """
        Отправка сообщения пользователю.
        """
        if not self.app:
            return False
        
        try:
            await self.app.bot.send_message(chat_id=chat_id, text=message)
            return True
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False
    
    async def shutdown(self):
        """
        Остановка бота.
        """
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()


telegram_bot_service = TelegramBotService()

