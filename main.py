import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from handlers import commands, conversation, calendar_handlers, fallback
from models.database import init_db, engine
from utils.config import BOT_TOKEN, WEBHOOK_URL, PORT
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(commands.router)
dp.include_router(conversation.router)
dp.include_router(calendar_handlers.router)
dp.include_router(fallback.router)

async def migrate_db():
    """Добавляет недостающие колонки в таблицу clients."""
    async with engine.begin() as conn:
        # Проверяем и добавляем колонку sphere
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clients' AND column_name='sphere'"))
        if not res.fetchone():
            await conn.execute(text("ALTER TABLE clients ADD COLUMN sphere VARCHAR"))
            logger.info("➕ Добавлена колонка sphere")
        # budget
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clients' AND column_name='budget'"))
        if not res.fetchone():
            await conn.execute(text("ALTER TABLE clients ADD COLUMN budget VARCHAR"))
            logger.info("➕ Добавлена колонка budget")
        # crm_need
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clients' AND column_name='crm_need'"))
        if not res.fetchone():
            await conn.execute(text("ALTER TABLE clients ADD COLUMN crm_need VARCHAR"))
            logger.info("➕ Добавлена колонка crm_need")
        # score
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clients' AND column_name='score'"))
        if not res.fetchone():
            await conn.execute(text("ALTER TABLE clients ADD COLUMN score INTEGER DEFAULT 0"))
            logger.info("➕ Добавлена колонка score")
        # cp_sent
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clients' AND column_name='cp_sent'"))
        if not res.fetchone():
            await conn.execute(text("ALTER TABLE clients ADD COLUMN cp_sent INTEGER DEFAULT 0"))
            logger.info("➕ Добавлена колонка cp_sent")
        # appointment_date
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clients' AND column_name='appointment_date'"))
        if not res.fetchone():
            await conn.execute(text("ALTER TABLE clients ADD COLUMN appointment_date VARCHAR"))
            logger.info("➕ Добавлена колонка appointment_date")

# Парсер временно отключён
# from parsers.telegram_parser import periodic_finding

async def on_startup():
    await init_db()
    await migrate_db()
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
