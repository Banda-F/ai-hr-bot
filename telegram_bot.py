import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Простая клавиатура
start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📝 Начать анкету")]],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🚀 Привет! Я AI-агент по подбору курьеров.\n"
        "Расскажу о вакансии и помогу устроиться.\n"
        "Нажми «Начать анкету», чтобы заполнить заявку.",
        reply_markup=start_kb
    )

@dp.message(F.text == "📝 Начать анкету")
async def start_anketa(message: types.Message):
    await message.answer("Пока что это демо-режим. Полная анкета появится позже.")

async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    print("Webhook установлен")

async def health(request):
    return web.Response(text="Bot is running")

def main():
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler
    
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path="/webhook")
    
    app.on_startup.append(lambda _: on_startup())
    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()