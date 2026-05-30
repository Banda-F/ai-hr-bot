import asyncio
import logging
from typing import Dict, Any, List

from source_parser import TelegramParser
from ai_analyzer import analyze_message

logger = logging.getLogger(__name__)

class ClientFinder:
    def __init__(self, bot, giga_client, config: Dict[str, Any]):
        self.bot = bot
        self.giga = giga_client
        self.config = config
        self.parser = TelegramParser(
            api_id=config["api_id"],
            api_hash=config["api_hash"],
            phone=config["phone"]
        )

    async def run_once(self):
        invited = 0
        try:
            await self.parser.connect()
            for channel in self.config["channels"]:
                if invited >= self.config["limit_per_run"]:
                    break
                messages = await self.parser.get_recent_messages(
                    channel,
                    minutes_back=self.config.get("minutes_back", 60)
                )
                for msg in messages:
                    if invited >= self.config["limit_per_run"]:
                        break
                    if len(msg["text"]) < 10:
                        continue
                    analysis = await analyze_message(self.giga, msg["text"])
                    if analysis.get("suitable"):
                        # Генерируем публичный ответ в чате
                        reply_text = (
                            "👋 Привет! Я занимаюсь разработкой AI-чат-ботов под ключ.\n"
                            "Могу помочь с вашей задачей. Напишите мне в личные сообщения @ваш_бот_username, "
                            "покажу примеры и цены. Либо оставьте заявку здесь: @ваш_бот_username\n"
                            "Жду обратной связи!"
                        )
                        try:
                            await self.bot.send_message(
                                chat_id=msg["chat_id"],
                                text=reply_text,
                                reply_to_message_id=msg["id"]
                            )
                            logger.info(f"Ответ опубликован в чате {channel} на сообщение {msg['id']}")
                            invited += 1
                            await asyncio.sleep(self.config.get("delay_between_invites", 60))
                        except Exception as e:
                            logger.error(f"Ошибка публикации ответа: {e}")
            await self.parser.disconnect()
        except Exception as e:
            logger.error(f"Ошибка в ClientFinder: {e}")
            await self.parser.disconnect()
