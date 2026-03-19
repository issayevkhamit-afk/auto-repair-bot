from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.catalog import LaborPrice, PartPrice
from pydantic import BaseModel

router = APIRouter()

class LaborPriceCreate(BaseModel):
    shop_id: int
    labor_key: str
    price: float
    hours: float

@router.post("/labor-prices/")
def add_labor_price(item: LaborPriceCreate, db: Session = Depends(get_db)):
    db_item = LaborPrice(
        shop_id=item.shop_id,
        labor_key=item.labor_key,
        price=item.price,
        hours=item.hours
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/labor-prices/{shop_id}")
def list_labor_prices(shop_id: int, db: Session = Depends(get_db)):
    return db.query(LaborPrice).filter(LaborPrice.shop_id == shop_id).all()
    
class PartPriceCreate(BaseModel):
    shop_id: int
    name: str
    avg_price: float
    category: str = None

@router.post("/part-prices/")
def add_part_price(item: PartPriceCreate, db: Session = Depends(get_db)):
    db_item = PartPrice(
        shop_id=item.shop_id,
        name=item.name,
        avg_price=item.avg_price,
        category=item.category
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/part-prices/{shop_id}")
def list_part_prices(shop_id: int, db: Session = Depends(get_db)):
    return db.query(PartPrice).filter(PartPrice.shop_id == shop_id).all()
