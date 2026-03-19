from sqlalchemy.orm import Session
from app.models.shop import Shop
from app.models.user import User
from app.models.catalog import LaborPrice, PartPrice, PartsCatalog
from app.models.market import MarketLaborPrice, MarketPartPrice, RegionMultiplier
from app.models.estimate import Estimate, EstimateItem
from app.schemas.estimate import ExtractedEstimateData
from app.services.normalization import normalize_labor_items
from app.core.i18n import t

def calculate_and_create_estimate(
    db: Session, 
    shop_id: int, 
    user_id: int, 
    extracted_data: ExtractedEstimateData
) -> Estimate:
    
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise ValueError("Shop not found")
        
    markup = shop.markup_percentage / 100.0 if shop.markup_percentage else 0.0
    
    # 1. Create Draft Estimate
    estimate = Estimate(
        shop_id=shop_id,
        user_id=user_id,
        car_make=extracted_data.car_make,
        car_model=extracted_data.car_model,
        car_year=extracted_data.car_year,
        notes=extracted_data.notes,
        status="draft"
    )
    db.add(estimate)
    db.flush() # Gain estimate.id
    
    total_labor = 0.0
    total_parts = 0.0
    has_manual_review = False
    market_pricing_used = False
    
    # 2. Process Labor Items
    normalized_labor = normalize_labor_items(db, shop_id, extracted_data)
    
    for lab in normalized_labor:
        est_item = EstimateItem(
            estimate_id=estimate.id,
            type="labor",
            description=lab["original_desc"],
            item_key=lab["labor_key"],
            quantity=lab["hours"] if lab["hours"] else 1.0, # default to 1.0 if not parsed
            unit_price=0.0,
            total=0.0,
            is_manual_review=True # default true until price found
        )
        
        if lab["labor_key"]:
            labor_price_row = db.query(LaborPrice).filter(
                LaborPrice.shop_id == shop_id,
                LaborPrice.labor_key == lab["labor_key"]
            ).first()
            
            if labor_price_row:
                est_item.unit_price = labor_price_row.price
                est_item.quantity = lab["hours"] if lab["hours"] else labor_price_row.hours
                est_item.total = est_item.unit_price * est_item.quantity
                est_item.is_manual_review = False
                total_labor += est_item.total
            else:
                market_labor = db.query(MarketLaborPrice).filter(MarketLaborPrice.labor_key == lab["labor_key"]).first()
                if market_labor:
                    multiplier = 1.0
                    if shop.city:
                        reg_mult = db.query(RegionMultiplier).filter(RegionMultiplier.city_name == shop.city).first()
                        if reg_mult:
                            multiplier = reg_mult.multiplier
                    
                    est_item.unit_price = market_labor.avg_price * multiplier
                    est_item.quantity = lab["hours"] if lab["hours"] else 1.0
                    est_item.total = est_item.unit_price * est_item.quantity
                    est_item.is_manual_review = False
                    est_item.description += " (Market)"
                    total_labor += est_item.total
                    market_pricing_used = True
                
        if est_item.is_manual_review:
            has_manual_review = True
            
        db.add(est_item)

    # 3. Process Part Items
    for part in extracted_data.part_items:
        est_item = EstimateItem(
            estimate_id=estimate.id,
            type="part",
            description=part.description,
            quantity=part.quantity if part.quantity else 1.0,
            unit_price=0.0,
            total=0.0,
            is_manual_review=True
        )
        
        # 3a. Find custom shop part price
        part_row = db.query(PartPrice).filter(
            PartPrice.shop_id == shop_id,
            PartPrice.name.ilike(f"%{part.description}%")
        ).first()
        
        if part_row:
            est_item.unit_price = part_row.avg_price * (1 + markup)
            est_item.total = est_item.unit_price * est_item.quantity
            est_item.is_manual_review = False
            total_parts += est_item.total
        else:
            # 3b. Find in PartsCatalog
            catalog_part = db.query(PartsCatalog).filter(PartsCatalog.name_ru.ilike(f"%{part.description}%")).first()
            if catalog_part:
                est_item.unit_price = catalog_part.avg_price * (1 + markup)
                est_item.total = est_item.unit_price * est_item.quantity
                est_item.is_manual_review = False
                est_item.description += " (Catalog)"
                total_parts += est_item.total
            else:
                # 3c. Find in MarketPartPrice
                market_part = db.query(MarketPartPrice).filter(MarketPartPrice.name_ru.ilike(f"%{part.description}%")).first()
                if market_part:
                    est_item.unit_price = market_part.avg_price * (1 + markup)
                    est_item.total = est_item.unit_price * est_item.quantity
                    est_item.is_manual_review = False
                    est_item.description += " (Market)"
                    total_parts += est_item.total
                    market_pricing_used = True
            
        if est_item.is_manual_review:
            has_manual_review = True
            
        db.add(est_item)
        
    estimate.total_labor = total_labor
    estimate.total_parts = total_parts
    estimate.grand_total = total_labor + total_parts
    
    if has_manual_review:
        estimate.status = "needs_confirmation"
        
    if market_pricing_used:
        user = db.query(User).filter(User.id == user_id).first()
        lang = user.language if user else shop.default_language
        disclaimer = t("disclaimer_market", lang)
        
        if estimate.notes:
            estimate.notes = estimate.notes + "\n\n" + disclaimer
        else:
            estimate.notes = disclaimer
        
    db.commit()
    db.refresh(estimate)
    
    return estimate
