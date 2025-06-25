# app/models/cart.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Cart(Base):
    __tablename__ = "carts"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Для зарегистрированных
    session_id = Column(String(255), nullable=True, index=True)                   # Для гостей
    
    # Время жизни корзины
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    # Ограничения
    __table_args__ = (
        CheckConstraint('user_id IS NOT NULL OR session_id IS NOT NULL', 
                       name='cart_must_have_user_or_session'),
    )
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, items_count={len(self.items)})>"
    
    @property
    def total_items(self):
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items)
    
    @property
    def total_amount(self):
        """Общая сумма корзины"""
        return sum(item.total_price for item in self.items)
    
    @property
    def total_weight(self):
        """Общий вес корзины"""
        total_weight = 0
        for item in self.items:
            if item.variant and item.variant.weight:
                total_weight += item.variant.weight * item.quantity
            elif item.product.weight:
                total_weight += item.product.weight * item.quantity
        return total_weight
    
    @property
    def is_empty(self):
        """Проверка, пуста ли корзина"""
        return len(self.items) == 0
    
    @property
    def stores_in_cart(self):
        """Получить список магазинов в корзине"""
        stores = {}
        for item in self.items:
            store = item.product.store
            if store.id not in stores:
                stores[store.id] = {
                    'store': store,
                    'items': [],
                    'total': 0
                }
            stores[store.id]['items'].append(item)
            stores[store.id]['total'] += item.total_price
        return list(stores.values())
    
    def get_item_by_product(self, product_id, variant_id=None):
        """Найти товар в корзине"""
        for item in self.items:
            if item.product_id == product_id and item.variant_id == variant_id:
                return item
        return None
    
    def clear_expired_items(self):
        """Очистить товары с истекшим сроком"""
        # Здесь можно добавить логику для удаления товаров,
        # которые больше недоступны или изменились в цене
        pass


class CartItem(Base):
    __tablename__ = "cart_items"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True, index=True)
    
    # Количество и цена
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(15, 2), nullable=False)  # Цена на момент добавления
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    variant = relationship("ProductVariant", back_populates="cart_items")
    
    # Ограничения
    __table_args__ = (
        CheckConstraint('quantity > 0', name='cart_item_positive_quantity'),
        UniqueConstraint('cart_id', 'product_id', 'variant_id', name='unique_cart_item'),
    )
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
    
    @property
    def total_price(self):
        """Общая стоимость позиции"""
        return self.price * self.quantity
    
    @property
    def current_price(self):
        """Текущая цена товара (может отличаться от цены в корзине)"""
        if self.variant:
            return self.variant.effective_price
        return self.product.price
    
    @property
    def price_changed(self):
        """Проверка, изменилась ли цена с момента добавления в корзину"""
        return float(self.price) != float(self.current_price)
    
    @property
    def is_available(self):
        """Проверка, доступен ли товар"""
        if self.variant:
            return (self.variant.is_active and 
                   self.variant.is_in_stock and 
                   self.product.is_published)
        return self.product.is_published and self.product.is_in_stock
    
    @property
    def stock_available(self):
        """Доступное количество на складе"""
        if self.variant:
            return self.variant.stock_quantity
        return self.product.stock_quantity
    
    @property
    def can_fulfill_quantity(self):
        """Может ли склад выполнить заказ в указанном количестве"""
        if not self.product.track_inventory:
            return True
        return self.stock_available >= self.quantity
    
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