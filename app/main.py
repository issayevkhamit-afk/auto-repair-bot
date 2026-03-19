import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from app.api.endpoints import webhook, admin
from app.core.database import engine, Base

# В реальном продакшн коде лучше использовать Alembic
# Но для быстрой демонстрации создаем таблицы если их нет:
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auto Repair Telegram Bot API", version="1.0.0")

app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.get("/")
def read_root():
    return {"status": "Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "OK"}
