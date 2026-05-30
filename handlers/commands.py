from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models.database import AsyncSessionLocal, Client
from sqlalchemy import select
from utils.config import ADMIN_CHAT_ID

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🤖 Привет! Я AI-бот, который создаёт AI-ботов для бизнеса.\n\n"
        "Я помогу автоматизировать ваш бизнес: сбор заявок, консультации, продажи 24/7.\n\n"
        "🔹 Узнать цены и варианты ботов: /price\n"
        "🔹 Посмотреть портфолио: /portfolio\n"
        "🔹 Связаться со мной: /contact\n\n"
        "Также я сам нахожу заказы в чатах – если вам нужен бот, просто напишите!",
        reply_markup=None  # можно добавить клавиатуру, если нужно
    )

@router.message(Command("price"))
async def price(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Базовый бот (опросник)", callback_data="price_basic")],
        [InlineKeyboardButton(text="🚀 AI-чат-бот (нейросеть)", callback_data="price_ai")],
        [InlineKeyboardButton(text="👑 Полный комплекс (бот + CRM)", callback_data="price_full")]
    ])
    await message.answer(
        "💰 *Варианты ботов и цены:*\n\n"
        "1️⃣ *Базовый бот-опросник* – от 30 000 ₽\n"
        "   ✅ Сбор заявок, анкетирование\n"
        "   ✅ Интеграция с Google Sheets\n"
        "   ✅ Уведомления менеджеру\n"
        "   ✅ Простая панель управления\n"
        "   ⏱ Срок: 3-5 дней\n\n"
        "2️⃣ *AI-чат-бот с нейросетью* – от 70 000 ₽\n"
        "   ✅ Умные ответы на вопросы клиентов\n"
        "   ✅ Контекстный диалог\n"
        "   ✅ Анализ настроений и интентов\n"
        "   ✅ Интеграция с GigaChat / ChatGPT\n"
        "   ⏱ Срок: 7-10 дней\n\n"
        "3️⃣ *Полный комплекс (бот + CRM + админка)* – от 150 000 ₽\n"
        "   ✅ Всё из Pro-пакета\n"
        "   ✅ Личный кабинет клиента для управления ботом\n"
        "   ✅ Расширенная аналитика и дашборды\n"
        "   ✅ Приоритетная поддержка 24/7\n"
        "   ⏱ Срок: 2-3 недели\n\n"
        "Точную цену назову после обсуждения задачи. /contact",
        parse_mode="Markdown",
        reply_markup=kb
    )

@router.message(Command("portfolio"))
async def portfolio(message: types.Message):
    await message.answer(
        "📁 *Портфолио:*\n\n"
        "• 🤖 *Бот для автоматического поиска клиентов* – парсинг Telegram-чатов + AI-анализ, приглашение подходящих кандидатов.\n"
        "• 💬 *AI-чат-бот для консультаций и продаж* – отвечает на вопросы, рекомендует товары, повышает конверсию.\n"
        "• 📝 *Бот для сбора заявок* – интеграция с Google Sheets, уведомления, админ-панель.\n"
        "• 🎓 *Бот-онбординг* – пошаговое обучение сотрудников или клиентов с проверкой прогресса.\n"
        "• 📅 *Бот для записи на услуги* – выбор времени, интеграция с Google Calendar, напоминания.\n\n"
        "Могу показать демо в работе. /contact для связи.",
        parse_mode="Markdown"
    )

@router.message(Command("stats"))
async def admin_stats(message: types.Message):
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
