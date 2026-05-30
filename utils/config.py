import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", 0))

GIGACHAT_BASE64 = os.getenv("GIGACHAT_BASE64")
GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "GigaChat")

GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./clients.db"
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

TG_API_ID = os.getenv("TG_API_ID")
TG_API_HASH = os.getenv("TG_API_HASH")
TG_PHONE = os.getenv("TG_PHONE")
PARSER_CHANNELS = os.getenv("PARSER_CHANNELS", "")
PARSER_LIMIT_PER_RUN = int(os.getenv("PARSER_LIMIT_PER_RUN", "3"))
PARSER_DELAY_SEC = int(os.getenv("PARSER_DELAY_SEC", "90"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "ваш_бот_username")