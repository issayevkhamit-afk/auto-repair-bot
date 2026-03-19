from sqlalchemy.orm import Session
from app.models.shop import Shop
from app.models.catalog import LaborPrice, PartPrice
from app.models.estimate import Estimate, EstimateItem
from app.schemas.estimate import ExtractedEstimateData
from app.services.normalization import normalize_labor_items

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
        
        # Find exact or like match in PartPrice
        part_row = db.query(PartPrice).filter(
            PartPrice.shop_id == shop_id,
            PartPrice.name.ilike(f"%{part.description}%")
        ).first()
        
        if part_row:
            # Apply markup
            est_item.unit_price = part_row.avg_price * (1 + markup)
            est_item.total = est_item.unit_price * est_item.quantity
            est_item.is_manual_review = False
            total_parts += est_item.total
            
        if est_item.is_manual_review:
            has_manual_review = True
            
        db.add(est_item)
        
    estimate.total_labor = total_labor
    estimate.total_parts = total_parts
    estimate.grand_total = total_labor + total_parts
    
    if has_manual_review:
        estimate.status = "needs_confirmation"
        
    db.commit()
    db.refresh(estimate)
    
    return estimate
