import logging
from aiogram import BaseMiddleware
from aiogram.types import Message

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        if isinstance(event, Message) and event.text:
            user = event.from_user
            username = user.username or f"{user.first_name} {user.last_name or ''}".strip()
            logging.info(f"Получено сообщение от {username} (ID: {user.id}): {event.text}")
        
        return await handler(event, data)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[
            logging.FileHandler("bot.log"),  # Логи сохраняем в файл bot.log
            logging.StreamHandler() 
        ]
    )