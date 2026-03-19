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
    
    for item in extracted_data.labor_items:
        clean_desc = normalize_text(item.description)
        matched_key = None
        
        # Exact match or substring search simple logic
        # Support comma separated synonyms for RU/KZ slang (e.g. 'замена масла, май ауыстыру')
        for alias in aliases:
            keywords = [normalize_text(k) for k in alias.keyword.split(',')]
            if any(k and k in clean_desc for k in keywords):
                matched_key = alias.labor_key
                break
                
        normalized_items.append({
            "type": "labor",
            "original_desc": item.description,
            "labor_key": matched_key, # None if not found
            "hours": item.hours
        })
        
    return normalized_items
