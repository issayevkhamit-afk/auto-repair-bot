from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class MarketLaborPrice(Base):
    __tablename__ = "market_labor_prices"

    id = Column(Integer, primary_key=True, index=True)
    labor_key = Column(String, index=True, nullable=False)
    name_ru = Column(String, nullable=False)
    name_kz = Column(String, nullable=False)
    category = Column(String, nullable=True)
    min_price = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    currency = Column(String, default="KZT")
    country = Column(String, default="KZ")
    city = Column(String, nullable=True)
    region_multiplier_group = Column(String, nullable=True)

class MarketPartPrice(Base):
    __tablename__ = "market_part_prices"

    id = Column(Integer, primary_key=True, index=True)
    part_key = Column(String, index=True, nullable=False)
    name_ru = Column(String, nullable=False)
    name_kz = Column(String, nullable=False)
    category = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    min_price = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    currency = Column(String, default="KZT")
    country = Column(String, default="KZ")
    city = Column(String, nullable=True)

class RegionMultiplier(Base):
    __tablename__ = "region_multipliers"
    
    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, index=True, nullable=False, unique=True)
    multiplier = Column(Float, nullable=False, default=1.0)
