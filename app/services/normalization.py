from sqlalchemy.orm import Session
from app.models.catalog import LaborAlias
from app.schemas.estimate import ExtractedEstimateData
import string

def normalize_text(text: str) -> str:
    # Basic normalization: lowercase, remove punctuation, strip
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def normalize_labor_items(db: Session, shop_id: int, extracted_data: ExtractedEstimateData):
    """
    Takes extracted labor items and attempts to map them to canonical labor_keys
    using the LaborAlias table for the given shop.
    Returns a list of dictionaries with mapped or unmapped labor data.
    """
    normalized_items = []
    
    aliases = db.query(LaborAlias).filter(LaborAlias.shop_id == shop_id).all()
    # Create a mapping dictionary for fast lookup
    alias_map = {normalize_text(alias.keyword): alias.labor_key for alias in aliases}
    
    for item in extracted_data.labor_items:
        clean_desc = normalize_text(item.description)
        matched_key = None
        
        # Exact match or substring search simple logic
        for keyword, lab_key in alias_map.items():
            if keyword in clean_desc:
                matched_key = lab_key
                break
                
        normalized_items.append({
            "type": "labor",
            "original_desc": item.description,
            "labor_key": matched_key, # None if not found
            "hours": item.hours
        })
        
    return normalized_items
