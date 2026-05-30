from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from services.ai_service import GigaChatAsync
from services.lead_scorer import score_lead
from utils.config import ADMIN_CHAT_ID
import json

router = Router()
giga = GigaChatAsync()

# Системный промпт для продающего AI
SYSTEM_PROMPT = """Ты — профессиональный AI-консультант по разработке чат-ботов. Твоя задача — помочь клиенту определиться с задачей и подвести его к заказу.

Правила:
- Отвечай дружелюбно, кратко, по делу.
- Если клиент спрашивает про цены или возможности — обязательно предложи посмотреть /price и /portfolio.
- Если клиент явно заинтересован (спрашивает про сроки, бюджет, интеграции), предложи заполнить анкету через /contact, чтобы получить персонализированное КП.
- Если клиент говорит что-то неопределённое, задай уточняющий вопрос: для какого бизнеса нужен бот, какой бюджет?
- После того как клиент заполнит анкету через /contact, бот сам отправит КП — тебе не нужно его генерировать.
- Старайся вести диалог к цели: получить контакты клиента.

Не навязывайся, но будь проактивным. Используй эмодзи для эмоций.
"""

@router.message()
async def sales_fallback(message: types.Message, state: FSMContext):
    # Проверяем, не находится ли пользователь в режиме анкетирования (FSM)
    current_state = await state.get_state()
    if current_state and current_state.startswith("SalesConversation"):
        # Не отвечаем, если уже идёт опрос
        return

    if not giga:
        await message.answer("Извините, я временно недоступен. Напишите /contact для связи.")
        return

    # Получаем историю диалога из состояния (или из Redis через state)
    user_data = await state.get_data()
    history = user_data.get("history", [])

    # Добавляем текущее сообщение пользователя в историю
    history.append({"role": "user", "content": message.text})

    # Ограничиваем длину истории (последние 10 сообщений)
    if len(history) > 10:
        history = history[-10:]

    # Формируем сообщения для GigaChat
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append(msg)

    # Генерируем ответ
    response = await giga.chat_with_system_messages(messages)  # нужно добавить метод в ai_service

    # Сохраняем ответ в историю
    history.append({"role": "assistant", "content": response})
    await state.update_data(history=history)

    await message.answer(response)