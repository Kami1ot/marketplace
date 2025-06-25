# app/models/order.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, DECIMAL, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class OrderStatus(str, enum.Enum):
    PENDING = "pending"          # Ожидает подтверждения
    CONFIRMED = "confirmed"      # Подтвержден
    PROCESSING = "processing"    # Обрабатывается
    SHIPPED = "shipped"          # Отправлен
    DELIVERED = "delivered"      # Доставлен
    CANCELLED = "cancelled"      # Отменен
    REFUNDED = "refunded"        # Возврат

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"          # Ожидает оплаты
    AUTHORIZED = "authorized"    # Авторизован
    PAID = "paid"               # Оплачен
    FAILED = "failed"           # Ошибка оплаты
    CANCELLED = "cancelled"     # Отменен
    REFUNDED = "refunded"       # Возвращен

class FulfillmentStatus(str, enum.Enum):
    UNFULFILLED = "unfulfilled"  # Не выполнен
    PARTIAL = "partial"          # Частично выполнен
    FULFILLED = "fulfilled"      # Выполнен

class PaymentMethod(str, enum.Enum):
    CARD = "card"                        # Банковская карта
    BANK_TRANSFER = "bank_transfer"      # Банковский перевод
    CASH_ON_DELIVERY = "cash_on_delivery" # Наложенный платеж
    DIGITAL_WALLET = "digital_wallet"    # Электронный кошелек

class ShipmentStatus(str, enum.Enum):
    PENDING = "pending"          # Ожидает отправки
    SHIPPED = "shipped"          # Отправлен
    IN_TRANSIT = "in_transit"    # В пути
    DELIVERED = "delivered"      # Доставлен
    FAILED = "failed"           # Ошибка доставки

class Order(Base):
    __tablename__ = "orders"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Может быть гостевой заказ
    
    # Контактная информация
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Статусы
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    fulfillment_status = Column(Enum(FulfillmentStatus), default=FulfillmentStatus.UNFULFILLED, nullable=False)
    
    # Финансовые данные
    subtotal = Column(DECIMAL(15, 2), nullable=False)           # Сумма товаров
    tax_amount = Column(DECIMAL(15, 2), default=0, nullable=False)     # Налоги
    shipping_amount = Column(DECIMAL(15, 2), default=0, nullable=False) # Доставка
    discount_amount = Column(DECIMAL(15, 2), default=0, nullable=False) # Скидки
    total_amount = Column(DECIMAL(15, 2), nullable=False)       # Итого
    currency = Column(String(3), default='RUB', nullable=False)
    
    # Заметки
    notes = Column(Text, nullable=True)
    
    # Адреса (JSON)
    shipping_address = Column(JSON, nullable=True)
    billing_address = Column(JSON, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Отношения
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("OrderShipment", back_populates="order", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="order")
    discount_usages = relationship("DiscountUsage", back_populates="order")
    
    def __repr__(self):
        return f"<Order(id={self.id}, number='{self.order_number}', status='{self.status}', total={self.total_amount})>"
    
    @property
    def is_guest_order(self):
        """Проверка, является ли заказ гостевым"""
        return self.user_id is None
    
    @property
    def customer_name(self):
        """Имя покупателя"""
        if self.user:
            return self.user.full_name
        return self.email.split('@')[0]
    
    @property
    def total_items(self):
        """Общее количество товаров в заказе"""
        return sum(item.quantity for item in self.items)
    
    @property
    def stores_in_order(self):
        """Магазины в заказе"""
        stores = {}
        for item in self.items:
            store_id = item.store_id
            if store_id not in stores:
                stores[store_id] = {
                    'store': item.store,
                    'items': [],
                    'subtotal': 0
                }
            stores[store_id]['items'].append(item)
            stores[store_id]['subtotal'] += item.total
        return list(stores.values())
    
    @property
    def can_be_cancelled(self):
        """Может ли заказ быть отменен"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
    
    @property
    def can_be_refunded(self):
        """Может ли быть возвращен"""
        return (self.status in [OrderStatus.DELIVERED, OrderStatus.SHIPPED] and 
                self.payment_status == PaymentStatus.PAID)
    
    @property
    def is_paid(self):
        """Проверка, оплачен ли заказ"""
        return self.payment_status == PaymentStatus.PAID
    
    @property
    def days_since_order(self):
        """Количество дней с момента заказа"""
        from datetime import datetime
        return (datetime.now(self.created_at.tzinfo) - self.created_at).days


class OrderItem(Base):
    __tablename__ = "order_items"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    
    # Количество и цены
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(15, 2), nullable=False)    # Цена за единицу на момент заказа
    total = Column(DECIMAL(15, 2), nullable=False)    # Общая стоимость позиции
    
    # Снимок товара на момент заказа
    product_snapshot = Column(JSON, nullable=True)  # Сохраняем данные товара
    
    # Временная метка
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Отношения
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    variant = relationship("ProductVariant", back_populates="order_items")
    store = relationship("Store", back_populates="order_items")
    reviews = relationship("Review", back_populates="order_item")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"
    
    @property
    def display_name(self):
        """Отображаемое название товара"""
        if self.product_snapshot and 'name' in self.product_snapshot:
            base_name = self.product_snapshot['name']
            if self.variant and 'variant_name' in self.product_snapshot:
                return f"{base_name} - {self.product_snapshot['variant_name']}"
            return base_name
        
        # Fallback к текущему товару
        if self.variant:
            return self.variant.display_name
        return self.product.name
    
    @property
    def can_be_reviewed(self):
        """Может ли быть оставлен отзыв"""
        return (self.order.status == OrderStatus.DELIVERED and 
                not any(r.status != "rejected" for r in self.reviews))


class Payment(Base):
    __tablename__ = "payments"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    
    # Метод и шлюз оплаты
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    gateway = Column(String(50), nullable=True)  # "stripe", "yandex", "sber"
    gateway_transaction_id = Column(String(255), nullable=True)
    
    # Финансовые данные
    amount = Column(DECIMAL(15, 2), nullable=False)
    currency = Column(String(3), default='RUB', nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Ответ от шлюза
    gateway_response = Column(JSON, nullable=True)
    
    # Временные метки
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    order = relationship("Order", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, amount={self.amount}, status='{self.status}')>"
    
    @property
    def is_successful(self):
        """Успешна ли оплата"""
        return self.status == PaymentStatus.PAID
    
    @property
    def is_pending(self):
        """Ожидает ли оплата обработки"""
        return self.status in [PaymentStatus.PENDING, PaymentStatus.AUTHORIZED]


class ShippingZone(Base):
    __tablename__ = "shipping_zones"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    countries = Column(JSON, nullable=True)  # Список стран
    regions = Column(JSON, nullable=True)    # Список регионов
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    shipping_methods = relationship("ShippingMethod", back_populates="zone", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ShippingZone(id={self.id}, name='{self.name}')>"


class ShippingMethod(Base):
    __tablename__ = "shipping_methods"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("shipping_zones.id"), nullable=False, index=True)
    
    # Информация о методе доставки
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(15, 2), nullable=False)
    free_threshold = Column(DECIMAL(15, 2), nullable=True)  # Бесплатная доставка от суммы
    estimated_days = Column(Integer, nullable=True)
    
    # Настройки
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    zone = relationship("ShippingZone", back_populates="shipping_methods")
    
    def __repr__(self):
        return f"<ShippingMethod(id={self.id}, name='{self.name}', price={self.price})>"
    
    def is_free_for_amount(self, amount):
        """Бесплатна ли доставка для указанной суммы"""
        return self.free_threshold and amount >= self.free_threshold


class OrderShipment(Base):
    __tablename__ = "order_shipments"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    
    # Информация о доставке
    tracking_number = Column(String(255), nullable=True, index=True)
    carrier = Column(String(100), nullable=True)  # "СДЭК", "Почта России"
    tracking_url = Column(Text, nullable=True)
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.PENDING, nullable=False)
    
    # Временные метки
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    order = relationship("Order", back_populates="shipments")
    
    def __repr__(self):
        return f"<OrderShipment(id={self.id}, order_id={self.order_id}, tracking='{self.tracking_number}')>"
    
    @property
    def is_trackable(self):
        """Можно ли отследить посылку"""
        return bool(self.tracking_number)
    
    @property
    def estimated_delivery_date(self):
        """Ожидаемая дата доставки"""
        if self.shipped_at and hasattr(self.order, 'shipping_method'):
            from datetime import timedelta
            estimated_days = getattr(self.order.shipping_method, 'estimated_days', 7)
            return self.shipped_at + timedelta(days=estimated_days)
        return None