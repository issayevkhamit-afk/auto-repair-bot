import os
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File, Response
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.shop import Shop, ShopAISettings, ShopPartsSettings
from app.models.catalog import LaborPrice, PartPrice
from app.models.user import User
from app.core.i18n import t
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_shop_admin

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates"))

def render(request: Request, template_name: str, context: dict):
    lang = request.cookies.get("lang", "ru")
    query_lang = request.query_params.get("lang")
    if query_lang in ["en", "ru", "kz"]:
        lang = query_lang
    context["request"] = request
    context["t"] = t
    context["lang"] = lang
    response = templates.TemplateResponse(template_name, context)
    if query_lang:
        response.set_cookie("lang", lang)
    return response

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render(request, "admin/login.html", {"error": None})


@router.get("/setup")
def setup_admin(db: Session = Depends(get_db)):
    """
    One-time setup endpoint — creates / resets the default superadmin to admin/123456.
    Accessible without authentication. Safe to run multiple times.
    Visit /admin/setup once after deployment to guarantee the admin user exists.
    """
    from app.models.shop import Shop
    from sqlalchemy import text as _text

    try:
        # Ensure platform shop exists
        master_shop = db.query(Shop).filter(Shop.name == "__platform__").first()
        if not master_shop:
            master_shop = Shop(name="__platform__", currency="KZT")
            db.add(master_shop)
            db.flush()   # get id without full commit

        new_hash = get_password_hash("123456")

        # Wipe any conflicting username="admin" entry first (keeps db clean)
        db.execute(_text(
            "UPDATE users SET username = NULL WHERE username = 'admin' AND telegram_id != '999999999'"
        ))
        db.flush()

        existing = db.execute(_text(
            "SELECT id FROM users WHERE telegram_id = '999999999'"
        )).fetchone()

        if existing:
            db.execute(_text(
                "UPDATE users SET username='admin', role='superadmin', status='active', "
                "hashed_password=:h WHERE telegram_id='999999999'"
            ), {"h": new_hash})
            msg = "updated"
        else:
            db.execute(_text(
                "INSERT INTO users (shop_id, telegram_id, username, role, language, status, hashed_password) "
                "VALUES (:sid, '999999999', 'admin', 'superadmin', 'ru', 'active', :h)"
            ), {"sid": master_shop.id, "h": new_hash})
            msg = "created"

        db.commit()
        return {
            "status": "ok",
            "message": f"Superadmin {msg}. Login at /admin/login",
            "username": "admin",
            "password": "123456",
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "detail": str(e)}

@router.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    print(f"LOGIN ATTEMPT: username='{username}'")
    
    # Look up by username first, fall back to telegram_id
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = db.query(User).filter(User.telegram_id == username).first()
    
    if not user:
        print("USER FOUND: None")
        return render(request, "admin/login.html", {"error": "User not found"})
    
    print(f"USER FOUND: username={user.username!r} telegram_id={user.telegram_id!r} role={user.role!r} status={user.status!r}")
    
    if user.role not in ["superadmin", "shop_admin"]:
        return render(request, "admin/login.html", {"error": f"Access denied. Role '{user.role}' is not allowed."})
    
    if not user.hashed_password:
        return render(request, "admin/login.html", {"error": "No password set. Contact platform admin."})
    
    pw_ok = verify_password(password, user.hashed_password)
    print(f"PASSWORD CHECK: plain='{password}' hash_prefix='{user.hashed_password[:20]}...' result={pw_ok}")
    
    if not pw_ok:
        return render(request, "admin/login.html", {"error": "Invalid password"})
        
    token = create_access_token(data={"sub": str(user.id)})
    if user.role == "superadmin":
        resp = RedirectResponse(url="/superadmin", status_code=303)
    else:
        resp = RedirectResponse(url=f"/admin/{user.shop_id}", status_code=303)
    resp.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return resp

@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/admin/login", status_code=303)
    resp.delete_cookie("access_token")
    return resp

@router.get("/{shop_id}", response_class=HTMLResponse)
def admin_dashboard(request: Request, shop_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_shop_admin)):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return render(request, "admin/dashboard.html", {"shop": shop, "current_user": current_user})

@router.post("/{shop_id}/update-shop")
def update_shop(
    request: Request,
    shop_id: int, 
    name: str = Form(...), 
    currency: str = Form(...), 
    default_language: str = Form(...),
    phone: str = Form(""),
    address: str = Form(""),
    city: str = Form(""),
    website: str = Form(""),
    whatsapp: str = Form(""),
    markup_percentage: float = Form(0.0),
    logo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_shop_admin)
):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if shop:
        shop.name = name
        shop.currency = currency
        shop.default_language = default_language
        shop.phone = phone
        shop.address = address
        shop.city = city
        shop.website = website
        shop.whatsapp = whatsapp
        shop.markup_percentage = markup_percentage
        
        if logo and logo.filename:
            ext = logo.filename.split(".")[-1].lower()
            if ext in ["jpg", "jpeg", "png", "webp"]:
                import uuid
                uid = uuid.uuid4().hex[:8]
                filename = f"shop_{shop_id}_{uid}.{ext}"
                target_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "uploads", "logos")
                os.makedirs(target_dir, exist_ok=True)
                file_path = os.path.join(target_dir, filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(logo.file.read())
                shop.logo_url = f"/static/uploads/logos/{filename}"
                
        db.commit()
    return RedirectResponse(url=f"/admin/{shop_id}", status_code=303)

@router.get("/{shop_id}/labor", response_class=HTMLResponse)
def admin_labor(request: Request, shop_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_shop_admin)):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    prices = db.query(LaborPrice).filter(LaborPrice.shop_id == shop_id).all()
    return render(request, "admin/labor.html", {"shop": shop, "prices": prices, "current_user": current_user})

@router.post("/{shop_id}/labor/upload")
async def admin_labor_upload(request: Request, shop_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_shop_admin)):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
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
def download_labor_template(shop_id: int, current_user: User = Depends(get_shop_admin)):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["labor_key", "price", "hours"])
    writer.writerow(["oil_change", "5000", "0.5"])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=labor_template.csv"})

@router.get("/{shop_id}/parts", response_class=HTMLResponse)
def admin_parts(request: Request, shop_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_shop_admin)):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    parts = db.query(PartPrice).filter(PartPrice.shop_id == shop_id).all()
    parts_settings = db.query(ShopPartsSettings).filter(ShopPartsSettings.shop_id == shop_id).first()
    if not parts_settings:
        parts_settings = ShopPartsSettings(shop_id=shop_id)
        db.add(parts_settings)
        db.commit()
    return render(request, "admin/parts.html", {"shop": shop, "parts": parts, "settings": parts_settings, "current_user": current_user})

@router.post("/{shop_id}/parts/upload")
async def admin_parts_upload(request: Request, shop_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_shop_admin)):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
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
def download_parts_template(shop_id: int, current_user: User = Depends(get_shop_admin)):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "avg_price", "category"])
    writer.writerow(["Oil Filter XYZ", "2500", "Filters"])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=parts_template.csv"})

@router.post("/{shop_id}/parts/settings")
def update_parts_settings(
    request: Request,
    shop_id: int,
    pricing_mode: str = Form("manual"),
    preferred_brands: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_shop_admin)
):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    settings = db.query(ShopPartsSettings).filter(ShopPartsSettings.shop_id == shop_id).first()
    if settings:
        settings.pricing_mode = pricing_mode
        settings.preferred_brands = preferred_brands
        db.commit()
    return RedirectResponse(url=f"/admin/{shop_id}/parts", status_code=303)
    
@router.get("/{shop_id}/ai", response_class=HTMLResponse)
def admin_ai(request: Request, shop_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_shop_admin)):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    ai_settings = db.query(ShopAISettings).filter(ShopAISettings.shop_id == shop_id).first()
    if not ai_settings:
        ai_settings = ShopAISettings(shop_id=shop_id)
        db.add(ai_settings)
        db.commit()
    return render(request, "admin/ai.html", {"shop": shop, "settings": ai_settings, "current_user": current_user})

@router.post("/{shop_id}/ai/update")
def update_ai(
    request: Request,
    shop_id: int,
    response_style: str = Form("standard"),
    price_range_display: str = Form("average"),
    custom_instruction: str = Form(""),
    include_disclaimer: str = Form("off"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_shop_admin)
):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    ai = db.query(ShopAISettings).filter(ShopAISettings.shop_id == shop_id).first()
    if ai:
        ai.response_style = response_style
        ai.price_range_display = price_range_display
        ai.custom_instruction = custom_instruction
        ai.include_disclaimer = True if include_disclaimer == "on" else False
        db.commit()
    return RedirectResponse(url=f"/admin/{shop_id}/ai", status_code=303)

@router.get("/{shop_id}/estimates", response_class=HTMLResponse)
def admin_estimates(request: Request, shop_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_shop_admin)):
    if current_user.role != "superadmin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    from app.models.estimate import Estimate
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    estimates = db.query(Estimate).filter(Estimate.shop_id == shop_id).order_by(Estimate.id.desc()).all()
    return render(request, "admin/estimates.html", {"shop": shop, "estimates": estimates, "current_user": current_user})

