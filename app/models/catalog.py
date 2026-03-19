from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class LaborPrice(Base):
    __tablename__ = "labor_prices"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    labor_key = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    hours = Column(Float, nullable=False)

    shop = relationship("Shop", back_populates="labor_prices")

class LaborAlias(Base):
    __tablename__ = "labor_aliases"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    keyword = Column(String, index=True, nullable=False)
    labor_key = Column(String, nullable=False)

    shop = relationship("Shop", back_populates="labor_aliases")

class PartPrice(Base):
    __tablename__ = "part_prices"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    avg_price = Column(Float, nullable=False)
    category = Column(String, nullable=True)

    shop = relationship("Shop", back_populates="part_prices")

class PartsCatalog(Base):
    __tablename__ = "parts_catalog"
    
    id = Column(Integer, primary_key=True, index=True)
    part_key = Column(String, index=True, nullable=False)
    name_ru = Column(String, nullable=False)
    name_kz = Column(String, nullable=False)
    category = Column(String, nullable=True)
    avg_price = Column(Float, nullable=False)
    preferred_brand = Column(String, nullable=True)
    notes = Column(String, nullable=True)

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    website = Column(String, nullable=True)
    
    supplier_links = relationship("SupplierLink", back_populates="supplier")

class SupplierLink(Base):
    __tablename__ = "supplier_links"
    
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    part_key = Column(String, index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    url = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    
    shop = relationship("Shop", back_populates="supplier_links")
    supplier = relationship("Supplier", back_populates="supplier_links")
