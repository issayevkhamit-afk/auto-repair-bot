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
