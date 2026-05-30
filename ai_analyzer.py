import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_CLIENT = """
Ты — AI-помощник для фрилансера, который создает AI-чат-ботов для бизнеса. Твоя задача: проанализировать сообщение в Telegram-чате и определить, является ли автор потенциальным клиентом для заказа разработки бота.

Критерии ПОДХОДЯЩЕГО клиента:
- Пользователь явно ищет разработчика ботов (фразы: "нужен бот", "сделайте бота", "разработка телеграм бота", "чат-бот для бизнеса", "автоматизация заявок").
- Пользователь спрашивает про цены, сроки, возможности ботов.
- Пользователь описывает свою бизнес-задачу, которую можно решить с помощью бота (например, сбор заявок, консультации, продажи).
- Сообщение содержит вопрос: "сколько стоит", "кто может сделать".

Критерии НЕПОДХОДЯЩЕГО клиента:
- Пользователь продаёт свои услуги (реклама).
- Сообщение не связано с разработкой ботов (общие вопросы, офтоп).
- Пользователь уже нашёл исполнителя и не ищет.

Важно: если в сообщении есть контакт (username, телефон) — укажи его. Если контакта нет, оставь null.

Ответ должен быть в формате JSON:
{
  "suitable": true/false,
  "username": "найденный_username или null",
  "reason": "краткое пояснение"
}
"""

async def analyze_message(client, message_text: str) -> Dict[str, Any]:
    if not client or not message_text:
        return {"suitable": False, "username": None, "reason": "Нет текста или AI недоступен"}
    try:
        response_text = await client.chat_with_system(message_text, SYSTEM_PROMPT_CLIENT)
        response_text = response_text.strip().replace('```json', '').replace('```', '')
        data = json.loads(response_text)
        return data
    except Exception as e:
        logger.error(f"Ошибка анализа сообщения: {e}")
        return {"suitable": False, "username": None, "reason": "Ошибка AI"}
