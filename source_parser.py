import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from telethon import TelegramClient
from telethon.errors import FloodWaitError

logger = logging.getLogger(__name__)

class TelegramParser:
    """
    Парсер публичных Telegram-каналов/чатов через Telethon.
    Требует наличия api_id, api_hash и телефонного номера (обычного аккаунта, не бота).
    """
    def __init__(self, api_id: int, api_hash: str, phone: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = TelegramClient('session_parser', api_id, api_hash)

    async def connect(self):
        await self.client.start(phone=self.phone)
        logger.info("TelegramParser подключён")

    async def disconnect(self):
        await self.client.disconnect()
        logger.info("TelegramParser отключён")

    async def get_recent_messages(self, channel_username: str, minutes_back: int = 60) -> List[Dict]:
        """
        Возвращает список сообщений из публичного канала за последние minutes_back минут.
        Каждое сообщение содержит:
        - id, text, date, sender_username, chat_id, chat_title
        """
        try:
            entity = await self.client.get_entity(channel_username)
            after_date = datetime.now() - timedelta(minutes=minutes_back)
            # Получаем до 200 сообщений, чтобы не пропустить свежие
            messages = await self.client.get_messages(entity, limit=200)
            result = []
            for msg in messages:
                if msg.date.replace(tzinfo=None) >= after_date and msg.text:
                    username = None
                    if msg.sender and hasattr(msg.sender, 'username'):
                        username = msg.sender.username
                    elif msg.from_id:
                        # Попытка получить username через get_entity (требует дополнительного запроса)
                        try:
                            sender_entity = await self.client.get_entity(msg.from_id)
                            username = sender_entity.username
                        except:
                            pass
                    result.append({
                        "id": msg.id,
                        "text": msg.text,
                        "date": msg.date,
                        "sender_username": username,
                        "chat_id": entity.id,
                        "chat_title": entity.title
                    })
            logger.info(f"Получено {len(result)} сообщений из {channel_username}")
            return result
        except FloodWaitError as e:
            logger.warning(f"Flood wait {e.seconds} секунд для канала {channel_username}")
            await asyncio.sleep(e.seconds)
            return []
        except Exception as e:
            logger.error(f"Ошибка парсинга {channel_username}: {e}")
            return []
