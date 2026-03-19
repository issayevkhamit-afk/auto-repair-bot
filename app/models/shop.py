from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    currency = Column(String, default="USD")
    markup_percentage = Column(Float, default=0.0)
    logo_url = Column(String, nullable=True)
    pdf_template_data = Column(Text, nullable=True)
    
    users = relationship("User", back_populates="shop")
    labor_prices = relationship("LaborPrice", back_populates="shop")
    labor_aliases = relationship("LaborAlias", back_populates="shop")
    part_prices = relationship("PartPrice", back_populates="shop")
    estimates = relationship("Estimate", back_populates="shop")
