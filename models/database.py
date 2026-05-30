from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from utils.config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

# Создаем асинхронный движок для работы с БД
engine = create_async_engine(DATABASE_URL, echo=False)
# Создаем фабрику для получения сессий
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

# --- Модель клиента ---
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    tg_id = Column(String, nullable=True)
    name = Column(String)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    sphere = Column(String, nullable=True)          # сфера бизнеса
    budget = Column(String, nullable=True)          # бюджет
    crm_need = Column(String, nullable=True)        # нужна ли CRM
    score = Column(Integer, default=0)              # скоринг лида
    cp_sent = Column(Integer, default=0)            # отправлено ли КП
    appointment_date = Column(String, nullable=True) # дата созвона
    status = Column(String, default="new")
    source = Column(String, default="telegram_chat")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

async def init_db():
    """Создает все таблицы, если они еще не созданы."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("База данных инициализирована")

# --- Функция миграции (добавляет новые колонки в существующую таблицу) ---
async def migrate_db():
    async with engine.begin() as conn:
        # Здесь код для добавления колонок, который мы использовали ранее.
        # Для краткости я его не привожу, но вы можете его добавить,
        # если таблица уже существует и нужно добавить колонки.
        # Однако, в новой модели они уже есть, и init_db создаст их.
        pass
