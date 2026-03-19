from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractedLaborItem(BaseModel):
    description: str = Field(..., description="Description of the labor task")
    hours: Optional[float] = Field(None, description="Extracted hours if mentioned")

class ExtractedPartItem(BaseModel):
    description: str = Field(..., description="Description of the part")
    quantity: Optional[float] = Field(1.0, description="Quantity of the part")
    brand: Optional[str] = Field(None, description="Brand of the part if mentioned")

class ExtractedEstimateData(BaseModel):
    car_make: Optional[str] = Field(None, description="Make of the car, e.g., Toyota")
    car_model: Optional[str] = Field(None, description="Model of the car, e.g., Camry")
    car_year: Optional[int] = Field(None, description="Year of the car, e.g., 2018")
    labor_items: List[ExtractedLaborItem] = Field(default_factory=list, description="List of labor items extracted")
    part_items: List[ExtractedPartItem] = Field(default_factory=list, description="List of part items extracted")
    notes: Optional[str] = Field(None, description="General notes or observations")
