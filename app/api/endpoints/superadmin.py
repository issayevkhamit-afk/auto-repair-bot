import os
import json
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.catalog import LaborPrice, PartPrice
from app.models.user import User
from app.models.shop import Shop
from app.models.estimate import Estimate
from app.models.system import GlobalAISettings, SystemLog, SubscriptionPlan
from app.models.market import MarketLaborPrice, MarketPartPrice, RegionMultiplier
from app.api.deps import get_superadmin
from app.api.endpoints.admin import render
from app.core.i18n import TRANSLATIONS_FILE, load_translations, save_translations

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_superadmin)):
    total_shops = db.query(Shop).count()
    total_users = db.query(User).count()
    total_estimates = db.query(Estimate).count()
    
    return render(request, "superadmin/dashboard.html", {
        "current_user": current_user,
        "total_shops": total_shops,
        "total_users": total_users,
        "total_estimates": total_estimates
    })

@router.get("/shops", response_class=HTMLResponse)
def manage_shops(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_superadmin)):
    shops = db.query(Shop).all()
    return render(request, "superadmin/shops.html", {
        "current_user": current_user,
        "shops": shops
    })

@router.get("/users", response_class=HTMLResponse)
def manage_users(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_superadmin)):
    users = db.query(User).all()
    return render(request, "superadmin/users.html", {
        "current_user": current_user,
        "users": users
    })

@router.get("/translations", response_class=HTMLResponse)
def manage_translations(request: Request, current_user: User = Depends(get_superadmin)):
    translations = load_translations()
    # Flatten structure for easy editing: key -> { 'en': val, 'ru': val, 'kz': val }
    keys = list(translations.get('ru', {}).keys())
    return render(request, "superadmin/translations.html", {
        "current_user": current_user,
        "translations": translations,
        "keys": keys
    })

@router.post("/translations/save")
async def save_translations_post(request: Request, current_user: User = Depends(get_superadmin)):
    form_data = await request.form()
    translations = load_translations()
    
    for field_name, value in form_data.items():
        if field_name.startswith("trans_"):
            parts = field_name.split("_", 2)
            if len(parts) == 3:
                lang = parts[1]
                key = parts[2]
                if lang not in translations:
                    translations[lang] = {}
                translations[lang][key] = value
                
    save_translations(translations)
    return RedirectResponse(url="/superadmin/translations", status_code=303)

@router.get("/estimates", response_class=HTMLResponse)
def manage_estimates(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_superadmin)):
    # Simple list of all estimates
    estimates = db.query(Estimate).order_by(Estimate.created_at.desc()).all() if hasattr(Estimate, 'created_at') else db.query(Estimate).order_by(Estimate.id.desc()).all()
@router.get("/ai", response_class=HTMLResponse)
def manage_ai(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_superadmin)):
    settings = db.query(GlobalAISettings).first()
    if not settings:
        settings = GlobalAISettings()
        db.add(settings)
        db.commit()
    return render(request, "superadmin/ai.html", {
        "current_user": current_user,
        "settings": settings
    })

@router.post("/ai/save")
def save_ai(
    request: Request, 
    system_prompt: str = Form(""),
    extraction_template: str = Form(""),
    pricing_rules: str = Form(""),
    model_name: str = Form("gpt-4o-mini"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_superadmin)
):
    settings = db.query(GlobalAISettings).first()
    if settings:
        settings.system_prompt = system_prompt
        settings.extraction_template = extraction_template
        settings.pricing_rules = pricing_rules
        settings.model_name = model_name
        db.commit()
    return RedirectResponse(url="/superadmin/ai", status_code=303)

@router.get("/market", response_class=HTMLResponse)
def manage_market(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_superadmin)):
    labor = db.query(MarketLaborPrice).all()
    parts = db.query(MarketPartPrice).all()
    regions = db.query(RegionMultiplier).all()
    return render(request, "superadmin/market.html", {
        "current_user": current_user,
        "labor": labor,
        "parts": parts,
        "regions": regions
    })

@router.get("/logs", response_class=HTMLResponse)
def view_logs(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_superadmin)):
    logs = db.query(SystemLog).order_by(SystemLog.created_at.desc()).limit(100).all() if hasattr(SystemLog, 'created_at') else db.query(SystemLog).order_by(SystemLog.id.desc()).limit(100).all()
    return render(request, "superadmin/logs.html", {
        "current_user": current_user,
        "logs": logs
    })
