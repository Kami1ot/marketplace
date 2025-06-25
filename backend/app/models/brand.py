# app/models/brand.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Brand(Base):
    __tablename__ = "brands"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    
    # Настройки
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    products = relationship("Product", back_populates="brand")
    
    def __repr__(self):
        return f"<Brand(id={self.id}, name='{self.name}', active={self.is_active})>"
    
    @property
    def products_count(self):
        """Количество активных товаров бренда"""
        return len([p for p in self.products if p.is_published])
    
    @property
    def display_name(self):
        """Отображаемое имя бренда"""
        return self.name
    
    @property
    def has_logo(self):
        """Есть ли логотип у бренда"""
        return bool(self.logo_url)
    
    @property
    def has_website(self):
        """Есть ли сайт у бренда"""
        return bool(self.website)
    
    def get_top_products(self, limit=5):
        """Получить топ товаров бренда (по популярности/продажам)"""
        # Здесь можно добавить логику сортировки по популярности
        return [p for p in self.products if p.is_published][:limit]
    
    def get_price_range(self):
        """Диапазон цен товаров бренда"""
        published_products = [p for p in self.products if p.is_published]
        if not published_products:
            return None
            
        prices = [p.price for p in published_products]
        return {
            "min": min(prices),
            "max": max(prices),
            "count": len(prices)
        }
    
    def get_categories(self):
        """Категории, в которых представлен бренд"""
        categories = set()
        for product in self.products:
            if product.is_published and product.category:
                categories.add(product.category)
        return list(categories)