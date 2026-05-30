from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
from services.calendar_api import create_meeting

router = Router()

@router.message(Command("available_slots"))
async def show_slots(message: types.Message):
    now = datetime.now()
    slots = []
    for i in range(1, 4):
        slot_time = now + timedelta(days=i)
        for hour in [11, 15, 17]:
            slot = slot_time.replace(hour=hour, minute=0, second=0, microsecond=0)
            if slot > now:
                slots.append(slot)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{slot.strftime('%d.%m %H:%M')}", callback_data=f"slot_{slot.isoformat()}")]
        for slot in slots[:5]
    ])
    await message.answer("Выберите удобное время для созвона:", reply_markup=kb)

@router.callback_query(F.data.startswith("slot_"))
async def slot_selected(callback: CallbackQuery):
    slot_iso = callback.data.split("_")[1]
    client_name = callback.from_user.first_name
    try:
        meet_link, event_link = await create_meeting(client_name, slot_iso)
        await callback.message.answer(
            f"✅ Встреча создана!\nСсылка для подключения: {meet_link}\nСобытие в календаре: {event_link}"
        )
    except Exception as e:
        logger.error(f"Ошибка создания встречи: {e}")
        await callback.message.answer(
            "❌ Не удалось создать встречу. Пожалуйста, свяжитесь с администратором."
        )
    await callback.answer()
