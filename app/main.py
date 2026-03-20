import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import webhook, admin, superadmin
from app.core.database import engine, Base, SessionLocal

Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

app = FastAPI(title="Auto Repair Telegram Bot API", version="1.0.0")

# Mount static folder for logo uploads
os.makedirs(os.path.join(os.path.dirname(__file__), "static", "uploads", "logos"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(superadmin.router, prefix="/superadmin", tags=["Superadmin"])


@app.on_event("startup")
def seed_superadmin():
    """Create a default superadmin user on first boot if none exists."""
    from app.models.user import User
    from app.models.shop import Shop
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.role == "superadmin").first()
        if existing:
            return  # already seeded

        # Need at least one shop for the FK — create a platform master shop
        master_shop = db.query(Shop).filter(Shop.name == "__platform__").first()
        if not master_shop:
            master_shop = Shop(name="__platform__", currency="KZT", status="active", plan="internal")
            db.add(master_shop)
            db.commit()
            db.refresh(master_shop)

        superadmin_user = User(
            shop_id=master_shop.id,
            telegram_id="999999999",
            role="superadmin",
            language="ru",
            status="active",
            hashed_password=get_password_hash("123456"),
        )
        db.add(superadmin_user)
        db.commit()
        logger.info("Default superadmin created: admin (telegram_id=999999999) / 123456")
        print("✅ Default superadmin created: telegram_id=999999999 / password=123456")
    except Exception as e:
        logger.error(f"Failed to seed superadmin: {e}", exc_info=True)
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"status": "Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "OK"}
