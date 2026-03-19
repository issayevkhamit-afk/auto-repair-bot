import os
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.shop import Shop, ShopAISettings, ShopPartsSettings
from app.models.catalog import LaborPrice, PartPrice

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates"))

@router.get("/{shop_id}", response_class=HTMLResponse)
def admin_dashboard(request: Request, shop_id: int, db: Session = Depends(get_db)):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "shop": shop})

@router.post("/{shop_id}/update-shop")
def update_shop(
    shop_id: int, 
    name: str = Form(...), 
    currency: str = Form(...), 
    default_language: str = Form(...),
    phone: str = Form(""),
    address: str = Form(""),
    city: str = Form(""),
    markup_percentage: float = Form(0.0),
    db: Session = Depends(get_db)
):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if shop:
        shop.name = name
        shop.currency = currency
        shop.default_language = default_language
        shop.phone = phone
        shop.address = address
        shop.city = city
        shop.markup_percentage = markup_percentage
        db.commit()
    return RedirectResponse(url=f"/admin/{shop_id}", status_code=303)

@router.get("/{shop_id}/labor", response_class=HTMLResponse)
def admin_labor(request: Request, shop_id: int, db: Session = Depends(get_db)):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    prices = db.query(LaborPrice).filter(LaborPrice.shop_id == shop_id).all()
    return templates.TemplateResponse("admin/labor.html", {"request": request, "shop": shop, "prices": prices})

@router.post("/{shop_id}/labor/upload")
async def admin_labor_upload(shop_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    for row in reader:
        labor_key = row.get("labor_key")
        price = float(row.get("price", 0))
        hours = float(row.get("hours", 0))
        if labor_key:
            existing = db.query(LaborPrice).filter(LaborPrice.shop_id == shop_id, LaborPrice.labor_key == labor_key).first()
            if existing:
                existing.price = price
                existing.hours = hours
            else:
                db.add(LaborPrice(shop_id=shop_id, labor_key=labor_key, price=price, hours=hours))
    db.commit()
    return RedirectResponse(url=f"/admin/{shop_id}/labor", status_code=303)

@router.get("/{shop_id}/labor/template")
def download_labor_template(shop_id: int):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["labor_key", "price", "hours"])
    writer.writerow(["oil_change", "5000", "0.5"])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=labor_template.csv"})

@router.get("/{shop_id}/parts", response_class=HTMLResponse)
def admin_parts(request: Request, shop_id: int, db: Session = Depends(get_db)):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    parts = db.query(PartPrice).filter(PartPrice.shop_id == shop_id).all()
    parts_settings = db.query(ShopPartsSettings).filter(ShopPartsSettings.shop_id == shop_id).first()
    if not parts_settings:
        parts_settings = ShopPartsSettings(shop_id=shop_id)
        db.add(parts_settings)
        db.commit()
    return templates.TemplateResponse("admin/parts.html", {"request": request, "shop": shop, "parts": parts, "settings": parts_settings})

@router.post("/{shop_id}/parts/upload")
async def admin_parts_upload(shop_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    for row in reader:
        name = row.get("name")
        avg_price = float(row.get("avg_price", 0))
        category = row.get("category", "")
        if name:
            existing = db.query(PartPrice).filter(PartPrice.shop_id == shop_id, PartPrice.name == name).first()
            if existing:
                existing.avg_price = avg_price
                existing.category = category
            else:
                db.add(PartPrice(shop_id=shop_id, name=name, avg_price=avg_price, category=category))
    db.commit()
    return RedirectResponse(url=f"/admin/{shop_id}/parts", status_code=303)

@router.get("/{shop_id}/parts/template")
def download_parts_template(shop_id: int):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "avg_price", "category"])
    writer.writerow(["Oil Filter XYZ", "2500", "Filters"])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=parts_template.csv"})

@router.post("/{shop_id}/parts/settings")
def update_parts_settings(
    shop_id: int,
    pricing_mode: str = Form("manual"),
    preferred_brands: str = Form(""),
    db: Session = Depends(get_db)
):
    settings = db.query(ShopPartsSettings).filter(ShopPartsSettings.shop_id == shop_id).first()
    if settings:
        settings.pricing_mode = pricing_mode
        settings.preferred_brands = preferred_brands
        db.commit()
    return RedirectResponse(url=f"/admin/{shop_id}/parts", status_code=303)
    
@router.get("/{shop_id}/ai", response_class=HTMLResponse)
def admin_ai(request: Request, shop_id: int, db: Session = Depends(get_db)):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    ai_settings = db.query(ShopAISettings).filter(ShopAISettings.shop_id == shop_id).first()
    if not ai_settings:
        ai_settings = ShopAISettings(shop_id=shop_id)
        db.add(ai_settings)
        db.commit()
    return templates.TemplateResponse("admin/ai.html", {"request": request, "shop": shop, "settings": ai_settings})

@router.post("/{shop_id}/ai/update")
def update_ai(
    shop_id: int,
    response_style: str = Form("standard"),
    price_range_display: str = Form("average"),
    custom_instruction: str = Form(""),
    include_disclaimer: str = Form("off"),
    db: Session = Depends(get_db)
):
    ai = db.query(ShopAISettings).filter(ShopAISettings.shop_id == shop_id).first()
    if ai:
        ai.response_style = response_style
        ai.price_range_display = price_range_display
        ai.custom_instruction = custom_instruction
        ai.include_disclaimer = True if include_disclaimer == "on" else False
        db.commit()
    return RedirectResponse(url=f"/admin/{shop_id}/ai", status_code=303)
