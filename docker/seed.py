import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Base, engine
from app.models.shop import Shop
from app.models.user import User
from app.models.catalog import LaborPrice, LaborAlias, PartPrice

def seed_db():
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if seed already exists
    if db.query(Shop).first():
        print("База уже заполнена.")
        return
        
    print("Добавление автосервиса и пользователя...")
    shop = Shop(name="Super Auto Service", currency="USD", markup_percentage=15.0)
    db.add(shop)
    db.commit()
    db.refresh(shop)
    
    user = User(shop_id=shop.id, telegram_id="123456789", role="admin") # Укажите свой telegram_id
    db.add(user)
    
    print("Добавление расценок...")
    labor1 = LaborPrice(shop_id=shop.id, labor_key="oil_change", price=50.0, hours=0.5)
    labor2 = LaborPrice(shop_id=shop.id, labor_key="brake_pads", price=120.0, hours=1.5)
    db.add_all([labor1, labor2])
    
    alias1 = LaborAlias(shop_id=shop.id, keyword="замена масла", labor_key="oil_change")
    alias2 = LaborAlias(shop_id=shop.id, keyword="масло поменять", labor_key="oil_change")
    alias3 = LaborAlias(shop_id=shop.id, keyword="колодки", labor_key="brake_pads")
    db.add_all([alias1, alias2, alias3])
    
    part1 = PartPrice(shop_id=shop.id, name="Oil Filter", avg_price=10.0, category="consumables")
    part2 = PartPrice(shop_id=shop.id, name="Brake Pads Set", avg_price=45.0, category="brakes")
    db.add_all([part1, part2])
    
    db.commit()
    print("Завершено!")

if __name__ == "__main__":
    seed_db()
