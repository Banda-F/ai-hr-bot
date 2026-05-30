from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from services.ai_service import GigaChatAsync
from services.lead_scorer import score_lead
from handlers.conversation import SalesConversation

router = Router()
giga = GigaChatAsync()

SYSTEM_PROMPT = """
Ты — профессиональный AI-консультант по разработке чат-ботов. Отвечай кратко, дружелюбно. Если клиент хочет купить бота, предложи заполнить анкету через /contact. Не отвечай на команды (они обрабатываются отдельно).
"""

@router.message()
async def sales_fallback(message: types.Message, state: FSMContext):
    # Игнорируем команды (они обрабатываются в других хендлерах)
    if message.text and message.text.startswith('/'):
        return

    # Если пользователь уже в процессе FSM (например, заполняет анкету) — не мешаем
    current_state = await state.get_state()
    if current_state and current_state.startswith("SalesConversation"):
        return

    # Анализируем намерение
    score_data = await score_lead(giga, message.text)
    if score_data.get("score") == 3:
        # Переключаем в FSM для сбора данных
        await state.set_state(SalesConversation.sphere)
        await message.answer("📝 Давайте уточним детали, чтобы подготовить лучшее предложение.\nДля какого бизнеса нужен бот?")
        return

    # Обычный AI-ответ
    response = await giga.chat_with_system(message.text, SYSTEM_PROMPT)
    await message.answer(response)
