from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Estimate(Base):
    __tablename__ = "estimates"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_make = Column(String, nullable=True)
    car_model = Column(String, nullable=True)
    car_year = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    status = Column(String, default="draft") # draft, needs_confirmation, approved
    
    total_labor = Column(Float, default=0.0)
    total_parts = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    shop = relationship("Shop", back_populates="estimates")
    user = relationship("User", back_populates="estimates")
    items = relationship("EstimateItem", back_populates="estimate", cascade="all, delete-orphan")
    ai_logs = relationship("AILog", back_populates="estimate", cascade="all, delete-orphan")

class EstimateItem(Base):
    __tablename__ = "estimate_items"

    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(Integer, ForeignKey("estimates.id"), nullable=False)
    type = Column(String, nullable=False) # labor or part
    item_key = Column(String, nullable=True)
    description = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    is_manual_review = Column(Boolean, default=False)

    estimate = relationship("Estimate", back_populates="items")

class AILog(Base):
    __tablename__ = "ai_logs"

    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(Integer, ForeignKey("estimates.id"), nullable=False)
    raw_input = Column(Text, nullable=False)
    extracted_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    estimate = relationship("Estimate", back_populates="ai_logs")
