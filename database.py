import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, func, select

# Путь к БД (SQLite)
DB_PATH = "sqlite+aiosqlite:///./candidates.db"

engine = create_async_engine(DB_PATH, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True)
    tg_id = Column(String, unique=True, nullable=True)   # Telegram ID кандидата
    vk_id = Column(String, unique=True, nullable=True)    # VK ID
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    city = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    experience = Column(Text, nullable=True)
    transport = Column(String, nullable=True)
    ready_date = Column(String, nullable=True)
    status = Column(String, default="new")  # new, contacted, documents_sent, registered, on_line, declined
    source = Column(String, nullable=True)  # откуда пришёл (telegram, parser, referral)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
class MessageLog(Base):
    __tablename__ = "message_logs"
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, nullable=False)
    direction = Column(String)  # incoming / outgoing
    text = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session