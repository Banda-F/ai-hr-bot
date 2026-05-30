import asyncio
import logging
from typing import Dict, Any, List

from source_parser import TelegramParser
from ai_analyzer import analyze_message

logger = logging.getLogger(__name__)

class CandidateFinder:
    """
    Оркестратор:
    - подключается к Telegram через Telethon,
    - собирает сообщения из заданных каналов,
    - анализирует через AI,
    - отправляет приглашения подходящим кандидатам (через бота).
    """
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
        """Один цикл: собрать сообщения -> анализ -> приглашения."""
        invited = 0
        try:
            await self.parser.connect()
            for channel in self.config["channels"]:
                if invited >= self.config["limit_per_run"]:
                    logger.info("Достигнут лимит приглашений за запуск")
                    break
                messages = await self.parser.get_recent_messages(
                    channel,
                    minutes_back=self.config.get("minutes_back", 60)
                )
                for msg in messages:
                    if invited >= self.config["limit_per_run"]:
                        break
                    # Пропускаем слишком короткие сообщения
                    if len(msg["text"]) < 10:
                        continue
                    analysis = await analyze_message(self.giga, msg["text"])
                    if analysis.get("suitable"):
                        # Если есть username – приглашаем напрямую
                        username = analysis.get("username") or msg.get("sender_username")
                        if username:
                            success = await self._send_invite(username, msg["text"][:200])
                            if success:
                                invited += 1
                                await asyncio.sleep(self.config.get("delay_between_invites", 60))
                            else:
                                logger.warning(f"Не удалось отправить приглашение @{username}")
                        else:
                            logger.info(f"Нет username для сообщения, пропускаем: {msg['text'][:50]}...")
            await self.parser.disconnect()
        except Exception as e:
            logger.error(f"Ошибка в работе CandidateFinder: {e}")
            await self.parser.disconnect()

    async def _send_invite(self, username: str, original_text: str) -> bool:
        """Отправляет личное сообщение пользователю через бота."""
        invite_text = (
            "👋 Привет! Я HR-бот партнёра Яндекс Еды.\n"
            "Вижу, вы ищете работу (или подработку). Хотите стать курьером?\n"
            "✅ Доход от 4000₽/день, гибкий график, оформление онлайн.\n"
            f"📝 Заполните анкету прямо сейчас: {self.config['bot_link']}?start=invite\n"
            "После этого я проведу вас по всем шагам до первой смены.\n\n"
            f"Ваше сообщение: \"{original_text[:100]}...\""
        )
        try:
            await self.bot.send_message(f"@{username}", invite_text)
            logger.info(f"Приглашение отправлено @{username}")
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки @{username}: {e}")
            return False
