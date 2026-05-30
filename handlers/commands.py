from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from utils.config import ADMIN_CHAT_ID
from models.database import AsyncSessionLocal, Client
from sqlalchemy import select, func

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🤖 Привет! Я AI-бот для создания AI-ботов.\n\n"
        "Я помогу автоматизировать ваш бизнес: сбор заявок, консультации, продажи 24/7.\n"
        "🔹 Примеры работ и цены: /price\n"
        "🔹 Портфолио: /portfolio\n"
        "🔹 Связаться со мной: /contact\n\n"
        "Также я сам нахожу заказы в чатах – если вам нужен бот, просто напишите!"
    )

@router.message(Command("price"))
async def price(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Базовый бот", callback_data="price_basic")],
        [InlineKeyboardButton(text="🚀 Бот с AI", callback_data="price_ai")],
        [InlineKeyboardButton(text="👑 Полный комплекс", callback_data="price_full")]
    ])
    await message.answer(
        "💰 *Цены на разработку ботов:*\n\n"
        "1️⃣ *Базовый бот-опросник* – от 30 000 ₽\n"
        "   - Сбор заявок, Google Sheets, уведомления.\n\n"
        "2️⃣ *AI-чат-бот с нейросетью* – от 70 000 ₽\n"
        "   - Умные ответы, анализ сообщений, интеграция с GigaChat.\n\n"
        "3️⃣ *Полный комплекс (бот + CRM + админка)* – от 150 000 ₽\n"
        "   - Всё, что нужно для продаж и поддержки.\n\n"
        "Точную цену назову после обсуждения задачи. /contact",
        parse_mode="Markdown",
        reply_markup=kb
    )

@router.message(Command("portfolio"))
async def portfolio(message: Message):
    await message.answer(
        "📁 *Портфолио:*\n\n"
        "• Бот для автоматического поиска клиентов (парсинг чатов + AI)\n"
        "• AI-чат-бот для консультаций и продаж\n"
        "• Бот для сбора заявок с интеграцией Google Sheets\n"
        "• Бот-онбординг с пошаговым обучением\n\n"
        "Могу показать демо в работе. /contact для связи.",
        parse_mode="Markdown"
    )

@router.message(Command("stats"))
async def admin_stats(message: Message):
    if message.from_user.id != ADMIN_CHAT_ID:
        await message.answer("Эта команда доступна только администратору.")
        return
    async with AsyncSessionLocal() as session:
        total = (await session.execute(select(Client))).scalars().all()
        total_count = len(total)
        new_count = len([c for c in total if c.status == "new"])
        contacted = len([c for c in total if c.status == "contacted"])
        negotiation = len([c for c in total if c.status == "negotiation"])
        closed = len([c for c in total if c.status == "closed"])
        await message.answer(
            f"📊 *Статистика CRM*\n"
            f"Всего клиентов: {total_count}\n"
            f"🆕 Новые: {new_count}\n"
            f"📞 Связались: {contacted}\n"
            f"🤝 Переговоры: {negotiation}\n"
            f"✅ Закрыто: {closed}",
            parse_mode="Markdown"
        )