import json
import logging
from services.ai_service import GigaChatAsync

logger = logging.getLogger(__name__)

async def score_lead(giga: GigaChatAsync, message_text: str) -> dict:
    prompt = f"""
Ты — система скоринга лидов для разработчика чат-ботов. Анализируй сообщение и верни только JSON:
{{
  "intent": "buy_bot" | "question" | "spam",
  "budget_hint": "low" | "mid" | "high" | "unknown",
  "score": 1 | 2 | 3,
  "reason": "кратко"
}}

Правила:
- Score 3: прямо хочет заказать бота, упоминает бюджет, сроки, сферу.
- Score 2: спрашивает про возможности, цены, но не говорит "хочу заказать".
- Score 1: просто комментарий без намерения купить.

Сообщение: {message_text}
"""
    try:
        response = await giga.chat_with_system(message_text, prompt)
        data = json.loads(response)
        return data
    except Exception as e:
        logger.error(f"Score error: {e}")
        return {"intent": "question", "budget_hint": "unknown", "score": 1, "reason": "ошибка"}