from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from utils.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    tg_id = Column(String, nullable=True)
    name = Column(String)
    phone = Column(String)
    company = Column(String, nullable=True)
    sphere = Column(String, nullable=True)      # сфера бизнеса
    budget = Column(String, nullable=True)      # бюджет
    crm_need = Column(String, nullable=True)    # нужна ли CRM
    score = Column(Integer, default=0)          # 1-3
    cp_sent = Column(Integer, default=0)        # 0/1
    appointment_date = Column(String, nullable=True)
    status = Column(String, default="new")
    source = Column(String, default="telegram_chat")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)