# app/models/product.py
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Связи
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # JSON поле для хранения URL изображений
    images = Column(JSON, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Отношения
    seller = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")