from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="mechanic") # admin or mechanic
    language = Column(String, default="ru") # ru, kz

    shop = relationship("Shop", back_populates="users")
    estimates = relationship("Estimate", back_populates="user")
