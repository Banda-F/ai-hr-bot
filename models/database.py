from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
