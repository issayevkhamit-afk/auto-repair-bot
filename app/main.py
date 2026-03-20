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
    """Ensure a default superadmin user with username='admin' always exists."""
    from app.models.user import User
    from app.models.shop import Shop
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        # Ensure the platform master shop exists
        master_shop = db.query(Shop).filter(Shop.name == "__platform__").first()
        if not master_shop:
            master_shop = Shop(name="__platform__", currency="KZT", status="active", plan="internal")
            db.add(master_shop)
            db.commit()
            db.refresh(master_shop)

        # Try to find by username first, then by telegram_id
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            user = db.query(User).filter(User.telegram_id == "999999999").first()

        if user:
            # Update existing user to ensure superadmin access and known password
            user.role = "superadmin"
            user.status = "active"
            user.username = "admin"
            user.hashed_password = get_password_hash("123456")
            db.commit()
            print("✅ Default superadmin updated: username=admin / password=123456")
        else:
            # Create fresh superadmin
            user = User(
                shop_id=master_shop.id,
                telegram_id="999999999",
                username="admin",
                role="superadmin",
                language="ru",
                status="active",
                hashed_password=get_password_hash("123456"),
            )
            db.add(user)
            db.commit()
            print("✅ Default superadmin created: username=admin / password=123456")

        logger.info("Ensured default superadmin exists: username=admin telegram_id=999999999 password=123456")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed superadmin: {e}", exc_info=True)
        print(f"❌ Superadmin seed failed: {e}")
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"status": "Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "OK"}
