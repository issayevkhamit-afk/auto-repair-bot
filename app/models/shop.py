from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    currency = Column(String, default="KZT")
    markup_percentage = Column(Float, default=0.0)
    logo_url = Column(String, nullable=True)
    pdf_template_data = Column(Text, nullable=True)
    
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    default_language = Column(String, default="ru")
    
    users = relationship("User", back_populates="shop")
    labor_prices = relationship("LaborPrice", back_populates="shop")
    labor_aliases = relationship("LaborAlias", back_populates="shop")
    part_prices = relationship("PartPrice", back_populates="shop")
    estimates = relationship("Estimate", back_populates="shop")

    supplier_links = relationship("SupplierLink", back_populates="shop")
    parts_settings = relationship("ShopPartsSettings", back_populates="shop", uselist=False)
    ai_settings = relationship("ShopAISettings", back_populates="shop", uselist=False)

class ShopPartsSettings(Base):
    __tablename__ = "shop_parts_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False, unique=True)
    pricing_mode = Column(String, default="manual") # manual, catalog, supplier_link
    
    shop = relationship("Shop", back_populates="parts_settings")

class ShopAISettings(Base):
    __tablename__ = "shop_ai_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False, unique=True)
    response_style = Column(String, default="detailed") # short, detailed
    show_price_ranges = Column(Boolean, default=False)
    num_part_options = Column(Integer, default=1)
    include_disclaimer = Column(Boolean, default=True)
    custom_instruction = Column(String, nullable=True)
    
    shop = relationship("Shop", back_populates="ai_settings")
