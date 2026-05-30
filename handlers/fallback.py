from aiogram import Router, types
from services.ai_service import GigaChatAsync
from services.lead_scorer import score_lead
from utils.config import ADMIN_CHAT_ID

router = Router()
giga = GigaChatAsync()

@router.message()
async def ai_response(message: types.Message):
    # Скоринг лида
    score_data = await score_lead(giga, message.text)
    if score_data.get("score") == 3 and ADMIN_CHAT_ID:
        await message.bot.send_message(
            ADMIN_CHAT_ID,
            f"🔥 *Горячий лид!* Score: 3\nСообщение: {message.text[:200]}\nОт: @{message.from_user.username or message.from_user.id}",
            parse_mode="Markdown"
        )
    # Генерируем ответ через AI
    system_prompt = (
        "Ты — AI-консультант по разработке чат-ботов. Отвечай дружелюбно, "
        "предлагай /price, /portfolio, /contact. Не навязывайся."
    )
    response = await giga.chat_with_system(message.text, system_prompt)
    await message.answer(response)