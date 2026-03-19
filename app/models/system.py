from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.database import Base

class GlobalAISettings(Base):
    __tablename__ = "global_ai_settings"

    id = Column(Integer, primary_key=True, index=True)
    system_prompt = Column(Text, nullable=True)
    extraction_template = Column(Text, nullable=True)
    pricing_rules = Column(Text, nullable=True)
    model_name = Column(String, default="gpt-4o-mini")
    fallback_settings = Column(Text, nullable=True)

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_type = Column(String, index=True) # ai, webhook, error, pdf
    message = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # trial, basic, pro
    price = Column(String, default="0") # KZT per month
    estimate_limit = Column(Integer, default=100) # per month
