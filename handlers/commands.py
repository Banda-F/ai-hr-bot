import os
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from models.database import AsyncSessionLocal, Client

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🤖 *Привет! Я AI-бот для создания AI-ботов.*\n\n"
        "Помогаю предпринимателям и бизнесам автоматизировать продажи, поддержку и сбор заявок с помощью Telegram-ботов.\n\n"
        "🔹 *Цены* – /price\n"
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
        "💰 *Выберите подходящий вариант:*\n\n"
        "1️⃣ *Базовый бот-опросник* – от 30 000 ₽\n"
        "   - Сбор заявок 24/7\n"
        "   - Интеграция с Google Sheets\n"
        "   - Уведомления в Telegram\n"
        "   - Простая панель управления\n\n"
        "2️⃣ *AI-чат-бот с нейросетью* – от 70 000 ₽\n"
        "   - Отвечает на вопросы клиентов автоматически\n"
        "   - Контекстный диалог (помнит, о чём говорили)\n"
        "   - Интеграция с GigaChat\n"
        "   - Помогает продавать 24/7\n\n"
        "3️⃣ *Полный комплекс (бот + CRM + админка)* – от 150 000 ₽\n"
        "   - Всё из пакета «Бот с AI»\n"
        "   - Личный кабинет клиента\n"
        "   - Расширенная аналитика и дашборды\n"
        "   - Приоритетная поддержка 24/7\n\n"
        "Нажмите на кнопку, чтобы узнать подробнее 👇",
        parse_mode="Markdown",
        reply_markup=kb
    )

@router.message(Command("portfolio"))
async def portfolio(message: types.Message):
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
async def admin_stats(message: types.Message):
    ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", 0))
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

@router.callback_query(lambda c: c.data.startswith("price_"))
async def price_callback(callback: types.CallbackQuery):
    if callback.data == "price_basic":
        text = (
            "📦 *Базовый бот* – от 30 000 ₽\n\n"
            "✅ *Что получите:*\n"
            "• Ваш бизнес работает 24/7 – заявки приходят даже ночью\n"
            "• Менеджеры не тратят время на ответы «сколько стоит?»\n"
            "• Все заявки в одной Google-таблице – удобно анализировать\n"
            "• Простая настройка под вашу сферу\n\n"
            "📅 Срок: 3–5 дней\n\n"
            "👉 Чтобы заказать, напишите /contact – я отвечу на все вопросы."
        )
    elif callback.data == "price_ai":
        text = (
            "🚀 *Бот с AI* – от 70 000 ₽\n\n"
            "✅ *Что получите:*\n"
            "• Искусственный интеллект отвечает клиентам как живой менеджер\n"
            "• Бот запоминает историю диалога – не нужно повторять одно и то же\n"
            "• Продажи идёт 24/7 – вы не теряете клиентов в нерабочее время\n"
            "• Интеграция с GigaChat – понимает сложные вопросы\n\n"
            "📅 Срок: 7–10 дней\n\n"
            "👉 Хотите так же? Напишите /contact – обсудим ваш бизнес."
        )
    else:
        text = (
            "👑 *Полный комплекс (бот + CRM + админка)* – от 150 000 ₽\n\n"
            "✅ *Что получите:*\n"
            "• Всё из пакета «Бот с AI»\n"
            "• Личный кабинет – смотрите статистику, меняйте ответы бота без программиста\n"
            "• Расширенная аналитика: конверсия, популярные вопросы, нагрузка\n"
            "• Приоритетная поддержка 24/7\n\n"
            "📅 Срок: 2–3 недели\n\n"
            "👉 Это решение для роста. /contact – запишемся на презентацию."
        )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()
