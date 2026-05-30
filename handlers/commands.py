from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🤖 *Привет! Я AI-бот для создания AI-ботов.*\n\n"
        "Помогаю предпринимателям и бизнесам автоматизировать продажи, поддержку и сбор заявок с помощью Telegram-ботов.\n\n"
        "🔹 *Примеры работ и цены* – /price\n"
        "🔹 *Портфолио* – /portfolio\n"
        "🔹 *Связаться со мной* – /contact\n\n"
        "_Просто напишите, что нужно – я отвечу и помогу подобрать решение._",
        parse_mode="Markdown"
    )

@router.message(Command("price"))
async def price(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Базовый бот", callback_data="price_basic")],
        [InlineKeyboardButton(text="🚀 Бот с AI", callback_data="price_ai")],
        [InlineKeyboardButton(text="👑 Полный комплекс", callback_data="price_full")]
    ])
    await message.answer(
        "💰 *Цены на разработку ботов:*\n\n"
        "1️⃣ *Базовый бот-опросник* – от 30 000 ₽\n"
        "   - Автоматический сбор заявок\n"
        "   - Интеграция с Google Sheets\n"
        "   - Уведомления менеджеру\n"
        "   - Простая панель управления\n"
        "   - Срок: 3–5 дней\n\n"
        "2️⃣ *AI-чат-бот с нейросетью* – от 70 000 ₽\n"
        "   - Умные ответы, анализ сообщений, интеграция с GigaChat\n"
        "   - Контекстный диалог\n"
        "   - Срок: 7–10 дней\n\n"
        "3️⃣ *Полный комплекс (бот + CRM + админка)* – от 150 000 ₽\n"
        "   - Всё из пакета «Бот с AI»\n"
        "   - Личный кабинет клиента для управления ботом\n"
        "   - Расширенная аналитика и дашборды\n"
        "   - Приоритетная поддержка 24/7\n"
        "   - Срок: 2–3 недели\n\n"
        "Точную цену назову после обсуждения задачи. /contact",
        parse_mode="Markdown",
        reply_markup=kb
    )

@router.message(Command("portfolio"))
async def portfolio(message: types.Message):
    await message.answer(
        "📁 *Портфолио:*\n\n"
        "• Бот для автоматического поиска клиентов (парсинг чатов + AI)\n"
        "• AI-чат-бот для консультаций и продаж\n"
        "• Бот для сбора заявок с интеграцией Google Sheets\n"
        "• Бот-онбординг с пошаговым обучением\n\n"
        "Могу показать демо в работе. /contact для связи.",
        parse_mode="Markdown"
    )

@router.callback_query(lambda c: c.data.startswith("price_"))
async def price_callback(callback: types.CallbackQuery):
    if callback.data == "price_basic":
        text = "📦 Базовый бот: от 30 000 ₽, срок 3–5 дней. Включает анкету, таблицу, уведомления."
    elif callback.data == "price_ai":
        text = "🚀 Бот с AI: от 70 000 ₽, срок 7–10 дней. Включает нейросеть, контекстный диалог."
    else:
        text = "👑 Полный комплекс: от 150 000 ₽, срок 2–3 недели. Включает CRM, админку, аналитику."
    await callback.message.answer(text + "\n\nЧтобы обсудить детали, напишите /contact.")
    await callback.answer()
