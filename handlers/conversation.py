from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from utils.config import ADMIN_CHAT_ID
from models.database import AsyncSessionLocal, Client
from services.ai_service import GigaChatAsync
import asyncio
from datetime import datetime

router = Router()
giga = GigaChatAsync()

class SalesConversation(StatesGroup):
    sphere = State()
    budget = State()
    crm_need = State()
    confirm_cp = State()

# Клавиатуры
yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
    resize_keyboard=True
)
confirm_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Да, отправить КП")]],
    resize_keyboard=True
)

@router.message(Command("contact"))
async def contact_start(message: Message, state: FSMContext):
    await state.set_state(SalesConversation.sphere)
    await message.answer(
        "📝 Давайте уточним детали, чтобы подготовить лучшее предложение.\n\n"
        "Для какого бизнеса или сферы нужен бот? (например: онлайн-школа, доставка, салон красоты)",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(SalesConversation.sphere)
async def ask_sphere(message: Message, state: FSMContext):
    await state.update_data(sphere=message.text)
    await state.set_state(SalesConversation.budget)
    await message.answer(
        "Какой бюджет планируете на разработку бота?\n"
        "(пример: до 50 000 ₽, 50-100 тыс ₽, более 150 тыс ₽)"
    )

@router.message(SalesConversation.budget)
async def ask_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await state.set_state(SalesConversation.crm_need)
    await message.answer(
        "Нужна ли интеграция с CRM (AmoCRM, Битрикс24, Яндекс.Метрика) или другими сервисами?",
        reply_markup=yes_no_kb
    )

@router.message(SalesConversation.crm_need)
async def ask_crm(message: Message, state: FSMContext):
    await state.update_data(crm_need=message.text)
    await state.set_state(SalesConversation.confirm_cp)
    await message.answer(
        "Спасибо! На основе ваших ответов я подготовлю коммерческое предложение.\n"
        "Отправить?",
        reply_markup=confirm_kb
    )

@router.message(SalesConversation.confirm_cp, F.text == "✅ Да, отправить КП")
async def send_cp(message: Message, state: FSMContext):
    data = await state.get_data()
    sphere = data.get("sphere", "не указано")
    budget = data.get("budget", "не указан")
    crm_need = data.get("crm_need", "не указано")
    user_id = message.from_user.id

    # Генерируем КП без Markdown (простой текст)
    cp_text = await generate_cp(sphere, budget, crm_need, user_id)
    # Отправляем как обычный текст (без parse_mode)
    await message.answer(cp_text)
    await message.answer(
        "📅 Также могу записать вас на бесплатный созвон (15–20 минут), где покажу примеры работ и отвечу на вопросы.\n"
        "Выберите удобное время: /available_slots"
    )
    await message.answer("✅ КП отправлено", reply_markup=ReplyKeyboardRemove())

    # Сохраняем данные в БД
    async with AsyncSessionLocal() as session:
        client = Client(
            tg_id=str(user_id),
            name=message.from_user.first_name,
            sphere=sphere,
            budget=budget,
            crm_need=crm_need,
            cp_sent=1,
            status="negotiation"
        )
        session.add(client)
        await session.commit()

    # Уведомление админу
    if ADMIN_CHAT_ID:
        await message.bot.send_message(
    ADMIN_CHAT_ID,
    f"📄 Новое КП отправлено\nКлиент: @{message.from_user.username or user_id}\nСфера: {sphere}\nБюджет: {budget}"
)
    await state.clear()

async def generate_cp(sphere: str, budget: str, crm_need: str, user_id: int) -> str:
    # Простая генерация из шаблонов (без Markdown)
    budget_lower = budget.lower()
    if "тыс" in budget_lower or "000" in budget_lower:
        if "50" in budget_lower or "100" in budget_lower:
            template = "pro"
        else:
            template = "enterprise"
    else:
        template = "starter"

    if template == "starter":
        return f"""
🤖 КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ

Сфера: {sphere}
Бюджет: {budget}

✅ Базовый чат-бот на Telegram
- Автоматический сбор заявок
- Интеграция с Google Sheets
- Уведомления менеджеру
- Простая панель управления

💰 Стоимость: от 30 000 ₽
⏱ Срок: 3-5 дней

Готовы обсудить детали? Напишите /contact
"""
    elif template == "pro":
        return f"""
🚀 КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ (PRO)

Сфера: {sphere}
Бюджет: {budget}
CRM интеграция: {crm_need}

✅ AI-чат-бот с нейросетью
- Умные ответы на вопросы клиентов
- Контекстный диалог
- Анализ настроений
- Интеграция с {crm_need if crm_need != 'Нет' else 'CRM по желанию'}

💰 Стоимость: от 70 000 ₽
⏱ Срок: 7-10 дней

Запишитесь на созвон: /available_slots
"""
    else:
        return f"""
👑 КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ (ENTERPRISE)

Сфера: {sphere}
Бюджет: {budget}
CRM интеграция: {crm_need}

✅ Полный комплекс (бот + CRM + веб-админка)
- Всё из Pro-пакета
- Личный кабинет клиента для управления ботом
- Расширенная аналитика и дашборды
- Приоритетная поддержка 24/7

💰 Стоимость: от 150 000 ₽
⏱ Срок: 2-3 недели

Персональная демонстрация: /available_slots
"""
