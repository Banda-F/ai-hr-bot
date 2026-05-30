import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from handlers import commands, conversation, calendar_handlers, fallback
from models.database import init_db
from utils.config import BOT_TOKEN, WEBHOOK_URL, PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(commands.router)
dp.include_router(conversation.router)
dp.include_router(calendar_handlers.router)
dp.include_router(fallback.router)

# Парсер временно отключён, так как отсутствует модуль parsers
# from parsers.telegram_parser import periodic_finding

async def on_startup():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(
        url=f"{WEBHOOK_URL}/webhook",
        allowed_updates=["message", "callback_query"]
    )
    logger.info(f"Webhook set to {WEBHOOK_URL}/webhook")
    # Парсер временно не запускаем
    # asyncio.create_task(periodic_finding())

async def health(request):
    return web.Response(text="OK")

def main():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    handler.register(app, path="/webhook")
    app.on_startup.append(lambda _: asyncio.create_task(on_startup()))
    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()