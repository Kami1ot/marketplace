# app/models/wishlist.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Wishlist(Base):
    __tablename__ = "wishlists"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Информация о списке
    name = Column(String(200), default='Избранное', nullable=False)
    is_default = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    user = relationship("User", back_populates="wishlists")
    items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Wishlist(id={self.id}, user_id={self.user_id}, name='{self.name}', items_count={len(self.items)})>"
    
    @property
    def total_items(self):
        """Общее количество товаров в списке желаний"""
        return len(self.items)
    
    @property
    def is_empty(self):
        """Проверка, пуст ли список желаний"""
        return len(self.items) == 0
    
    @property
    def available_items(self):
        """Товары, которые доступны для покупки"""
        return [item for item in self.items if item.is_available]
    
    @property
    def total_value(self):
        """Общая стоимость товаров в списке"""
        return sum(item.current_price for item in self.available_items)
    
    def has_product(self, product_id, variant_id=None):
        """Проверить, есть ли товар в списке"""
        for item in self.items:
            if item.product_id == product_id and item.variant_id == variant_id:
                return True
        return False
    
    def get_item_by_product(self, product_id, variant_id=None):
        """Найти товар в списке"""
        for item in self.items:
            if item.product_id == product_id and item.variant_id == variant_id:
                return item
        return None


class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    wishlist_id = Column(Integer, ForeignKey("wishlists.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True, index=True)
    
    # Временная метка
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Отношения
    wishlist = relationship("Wishlist", back_populates="items")
    product = relationship("Product", back_populates="wishlist_items")
    variant = relationship("ProductVariant", back_populates="wishlist_items")
    
    # Уникальные ограничения
    __table_args__ = (
        UniqueConstraint('wishlist_id', 'product_id', 'variant_id', name='unique_wishlist_item'),
    )
    
    def __repr__(self):
        return f"<WishlistItem(id={self.id}, wishlist_id={self.wishlist_id}, product_id={self.product_id})>"
    
    @property
    def current_price(self):
        """Текущая цена товара"""
        if self.variant:
            return self.variant.effective_price
        return self.product.price
    
    @property
    def compare_price(self):
        """Зачеркнутая цена товара"""
        if self.variant:
            return self.variant.effective_compare_price
        return self.product.compare_price
    
    @property
    def is_available(self):
        """Проверка, доступен ли товар"""
        if self.variant:
            return (self.variant.is_active and 
                   self.variant.is_in_stock and 
                   self.product.is_published)
        return self.product.is_published and self.product.is_in_stock
    
    @property
    def is_on_sale(self):
        """Проверка, есть ли скидка на товар"""
        compare_price = self.compare_price
        current_price = self.current_price
        return compare_price and compare_price > current_price
    
    @property
    def discount_percentage(self):
        """Процент скидки"""
        if self.variant:
            return self.variant.discount_percentage
        return self.product.discount_percentage
    
    @property
    def display_name(self):
        """Отображаемое название товара"""
        if self.variant:
            return self.variant.display_name
        return self.product.name
    
    @property
    def image_url(self):
        """URL изображения товара"""
        if self.variant and self.variant.images:
            return self.variant.images[0].url
        elif self.product.main_image:
            return self.product.main_image.url
        return None
    
    @property
    def stock_status(self):
        """Статус наличия товара"""
        if not self.is_available:
            return "unavailable"
        
        if self.variant:
            stock = self.variant.stock_quantity
            is_low = self.variant.is_low_stock
        else:
            stock = self.product.stock_quantity
            is_low = self.product.is_low_stock
        
        if stock == 0:
            return "out_of_stock"
        elif is_low:
            return "low_stock"
        else:
            return "in_stock"