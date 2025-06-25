# app/models/product.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, DECIMAL, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ProductStatus(str, enum.Enum):
    DRAFT = "draft"          # Черновик
    ACTIVE = "active"        # Активный
    INACTIVE = "inactive"    # Неактивный
    ARCHIVED = "archived"    # Архивированный

class ProductVisibility(str, enum.Enum):
    PUBLISHED = "published"              # Опубликован
    HIDDEN = "hidden"                   # Скрыт
    PASSWORD_PROTECTED = "password_protected"  # Защищен паролем

class Product(Base):
    __tablename__ = "products"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True, index=True)
    
    # Идентификация
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(300), nullable=False, index=True)
    slug = Column(String(300), unique=True, nullable=False, index=True)
    
    # Описание
    description = Column(Text, nullable=True)
    short_description = Column(Text, nullable=True)
    
    # Цены и стоимость
    price = Column(DECIMAL(15, 2), nullable=False, index=True)
    compare_price = Column(DECIMAL(15, 2), nullable=True)  # Зачеркнутая цена
    cost_price = Column(DECIMAL(15, 2), nullable=True)     # Себестоимость
    
    # Физические характеристики
    weight = Column(DECIMAL(8, 3), nullable=True)  # Вес в кг
    dimensions = Column(JSON, nullable=True)        # {"length": 10, "width": 5, "height": 2}
    
    # Статусы
    status = Column(Enum(ProductStatus), default=ProductStatus.DRAFT, nullable=False, index=True)
    visibility = Column(Enum(ProductVisibility), default=ProductVisibility.PUBLISHED, nullable=False)
    
    # Управление запасами
    track_inventory = Column(Boolean, default=True, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False, index=True)
    low_stock_threshold = Column(Integer, default=5, nullable=False)
    allow_backorder = Column(Boolean, default=False, nullable=False)
    
    # SEO поля
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    
    # Дополнительные характеристики и теги
    attributes = Column(JSON, nullable=True)  # {"color": "red", "size": "XL", "material": "cotton"}
    tags = Column(JSON, nullable=True)        # ["новинка", "скидка", "хит"]
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Отношения
    store = relationship("Store", back_populates="products")
    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="product")
    wishlist_items = relationship("WishlistItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    views = relationship("ProductView", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price}, status='{self.status}')>"
    
    @property
    def is_published(self):
        """Проверка, опубликован ли товар"""
        return (self.status == ProductStatus.ACTIVE and 
                self.visibility == ProductVisibility.PUBLISHED and 
                self.published_at is not None)
    
    @property
    def is_in_stock(self):
        """Проверка наличия на складе"""
        if not self.track_inventory:
            return True
        if self.variants:
            # Если есть варианты, проверяем их запасы
            return any(variant.is_in_stock for variant in self.variants if variant.is_active)
        return self.stock_quantity > 0 or self.allow_backorder
    
    @property
    def is_low_stock(self):
        """Проверка низкого остатка"""
        if not self.track_inventory:
            return False
        if self.variants:
            return all(variant.stock_quantity <= variant.product.low_stock_threshold 
                      for variant in self.variants if variant.is_active)
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def main_image(self):
        """Главное изображение товара"""
        main_images = [img for img in self.images if img.is_main and not img.variant_id]
        return main_images[0] if main_images else None
    
    @property
    def all_images(self):
        """Все изображения товара (основные + варианты)"""
        return [img for img in self.images if not img.variant_id]
    
    @property
    def discount_percentage(self):
        """Процент скидки"""
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    @property
    def effective_price(self):
        """Эффективная цена (минимальная среди вариантов или основная)"""
        if self.variants:
            variant_prices = [v.effective_price for v in self.variants if v.is_active]
            return min(variant_prices) if variant_prices else self.price
        return self.price
    
    @property
    def price_range(self):
        """Диапазон цен для товара с вариантами"""
        if not self.variants:
            return None
        
        active_variants = [v for v in self.variants if v.is_active]
        if not active_variants:
            return None
            
        prices = [v.effective_price for v in active_variants]
        min_price, max_price = min(prices), max(prices)
        
        if min_price == max_price:
            return None
        return {"min": min_price, "max": max_price}
    
    @property
    def total_stock(self):
        """Общий запас товара"""
        if self.variants:
            return sum(v.stock_quantity for v in self.variants if v.is_active)
        return self.stock_quantity
    
    @property
    def reviews_summary(self):
        """Сводка по отзывам"""
        approved_reviews = [r for r in self.reviews if r.status == "approved"]
        if not approved_reviews:
            return {"count": 0, "average": 0, "ratings": {}}
        
        total = len(approved_reviews)
        average = sum(r.rating for r in approved_reviews) / total
        
        ratings = {}
        for i in range(1, 6):
            ratings[str(i)] = len([r for r in approved_reviews if r.rating == i])
        
        return {
            "count": total,
            "average": round(average, 1),
            "ratings": ratings
        }


class ProductVariant(Base):
    __tablename__ = "product_variants"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Идентификация варианта
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=True)  # "Красный XL", "128GB"
    
    # Цены (могут отличаться от основного товара)
    price = Column(DECIMAL(15, 2), nullable=True)
    compare_price = Column(DECIMAL(15, 2), nullable=True)
    
    # Запасы
    stock_quantity = Column(Integer, default=0, nullable=False)
    weight = Column(DECIMAL(8, 3), nullable=True)
    
    # Характеристики варианта
    attributes = Column(JSON, nullable=True)  # {"color": "red", "size": "XL"}
    
    # Главное изображение варианта
    image_id = Column(Integer, nullable=True)  # Ссылка на ProductImage.id
    
    # Настройки
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    product = relationship("Product", back_populates="variants")
    cart_items = relationship("CartItem", back_populates="variant")
    wishlist_items = relationship("WishlistItem", back_populates="variant")
    order_items = relationship("OrderItem", back_populates="variant")
    images = relationship("ProductImage", back_populates="variant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ProductVariant(id={self.id}, product_id={self.product_id}, name='{self.name}', sku='{self.sku}')>"
    
    @property
    def effective_price(self):
        """Эффективная цена (цена варианта или цена товара)"""
        return self.price if self.price is not None else self.product.price
    
    @property
    def effective_compare_price(self):
        """Эффективная зачеркнутая цена"""
        return self.compare_price if self.compare_price is not None else self.product.compare_price
    
    @property
    def is_in_stock(self):
        """Проверка наличия варианта на складе"""
        if not self.product.track_inventory:
            return True
        return self.stock_quantity > 0 or self.product.allow_backorder
    
    @property
    def is_low_stock(self):
        """Проверка низкого остатка варианта"""
        if not self.product.track_inventory:
            return False
        return self.stock_quantity <= self.product.low_stock_threshold
    
    @property
    def display_name(self):
        """Отображаемое имя варианта"""
        if self.name:
            return f"{self.product.name} - {self.name}"
        return self.product.name
    
    @property
    def discount_percentage(self):
        """Процент скидки варианта"""
        compare_price = self.effective_compare_price
        current_price = self.effective_price
        if compare_price and compare_price > current_price:
            return round(((compare_price - current_price) / compare_price) * 100)
        return 0


class ProductImage(Base):
    __tablename__ = "product_images"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True, index=True)
    
    # Информация об изображении
    url = Column(Text, nullable=False)
    alt_text = Column(String(255), nullable=True)
    
    # Настройки
    sort_order = Column(Integer, default=0, nullable=False)
    is_main = Column(Boolean, default=False, nullable=False)  # Главное изображение
    
    # Временная метка
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Отношения
    product = relationship("Product", back_populates="images")
    variant = relationship("ProductVariant", back_populates="images")
    
    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, is_main={self.is_main})>"
    
    @property
    def belongs_to_variant(self):
        """Проверка, принадлежит ли изображение варианту"""
        return self.variant_id is not None
    
    @property
    def belongs_to_product(self):
        """Проверка, принадлежит ли изображение основному товару"""
        return self.variant_id is None
    
    @property
    def effective_alt_text(self):
        """Эффективный alt текст"""
        if self.alt_text:
            return self.alt_text
        if self.variant:
            return f"{self.product.name} - {self.variant.name}"
        return self.product.name