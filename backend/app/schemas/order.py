# app/schemas/order.py
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum

# === ENUMS ===

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class FulfillmentStatus(str, Enum):
    UNFULFILLED = "unfulfilled"
    PARTIAL = "partial"
    FULFILLED = "fulfilled"

class PaymentMethod(str, Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"
    DIGITAL_WALLET = "digital_wallet"

class ShipmentStatus(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"

class OrderSort(str, Enum):
    CREATED_DESC = "created_desc"
    CREATED_ASC = "created_asc"
    TOTAL_DESC = "total_desc"
    TOTAL_ASC = "total_asc"
    STATUS = "status"

# === ADDRESS SCHEMAS ===

class AddressSchema(BaseModel):
    """Схема для адреса"""
    country: str
    region: Optional[str] = None
    city: str
    street: str
    building: Optional[str] = None
    apartment: Optional[str] = None
    postal_code: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {"lat": 55.123, "lng": 37.456}
    
class ContactInfo(BaseModel):
    """Контактная информация"""
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None

# === ORDER SCHEMAS ===

class OrderBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    notes: Optional[str] = None
    shipping_address: Optional[AddressSchema] = None
    billing_address: Optional[AddressSchema] = None

class OrderCreate(OrderBase):
    """Схема для создания заказа"""
    user_id: Optional[int] = None
    items: List['OrderItemCreate']
    shipping_method_id: Optional[int] = None
    discount_codes: Optional[List[str]] = None

class OrderUpdate(BaseModel):
    """Схема для обновления заказа"""
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    fulfillment_status: Optional[FulfillmentStatus] = None
    notes: Optional[str] = None
    shipping_address: Optional[AddressSchema] = None
    billing_address: Optional[AddressSchema] = None

class OrderResponse(OrderBase):
    """Схема для ответа с заказом"""
    id: int
    order_number: str
    user_id: Optional[int] = None
    status: OrderStatus
    payment_status: PaymentStatus
    fulfillment_status: FulfillmentStatus
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    is_guest_order: bool
    customer_name: str
    total_items: int
    can_be_cancelled: bool
    can_be_refunded: bool
    is_paid: bool
    days_since_order: int
    
    class Config:
        from_attributes = True

class OrderSimple(BaseModel):
    """Упрощенная схема заказа"""
    id: int
    order_number: str
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    customer_name: str
    
    class Config:
        from_attributes = True

class OrderWithItems(OrderResponse):
    """Заказ с товарами"""
    items: List['OrderItemResponse'] = []
    
    class Config:
        from_attributes = True

class OrderWithPayments(OrderResponse):
    """Заказ с платежами"""
    payments: List['PaymentResponse'] = []
    
    class Config:
        from_attributes = True

class OrderWithShipments(OrderResponse):
    """Заказ с отправками"""
    shipments: List['OrderShipmentResponse'] = []
    
    class Config:
        from_attributes = True

class OrderFull(OrderResponse):
    """Полная информация о заказе"""
    items: List['OrderItemResponse'] = []
    payments: List['PaymentResponse'] = []
    shipments: List['OrderShipmentResponse'] = []
    user: Optional['UserSimple'] = None
    
    class Config:
        from_attributes = True

class OrderFinancials(BaseModel):
    """Финансовая сводка заказа"""
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str
    savings: Decimal  # Общая экономия
    tax_rate: Optional[float] = None
    
    class Config:
        from_attributes = True

class OrderTimeline(BaseModel):
    """Временная линия заказа"""
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    """Обновление статуса заказа"""
    status: OrderStatus
    message: Optional[str] = None
    notify_customer: bool = True

class OrderList(BaseModel):
    """Схема для списка заказов с пагинацией"""
    orders: List[OrderResponse]
    total: int
    page: int
    size: int
    pages: int
    total_amount: Decimal  # Общая сумма заказов на странице

class OrderFilter(BaseModel):
    """Схема для фильтрации заказов"""
    user_id: Optional[int] = None
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    fulfillment_status: Optional[FulfillmentStatus] = None
    order_number: Optional[str] = None
    email: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    amount_min: Optional[Decimal] = Field(None, ge=0)
    amount_max: Optional[Decimal] = Field(None, ge=0)
    search: Optional[str] = None  # Поиск по номеру заказа, email, товарам

# === ORDER ITEM SCHEMAS ===

class OrderItemBase(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    store_id: int
    quantity: int = Field(..., gt=0)
    price: Decimal = Field(..., gt=0, decimal_places=2)

class OrderItemCreate(BaseModel):
    """Схема для создания позиции заказа"""
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(..., gt=0)

class OrderItemResponse(OrderItemBase):
    """Схема для ответа с позицией заказа"""
    id: int
    order_id: int
    total: Decimal
    product_snapshot: Optional[Dict[str, Any]] = None
    created_at: datetime
    display_name: str
    can_be_reviewed: bool
    
    class Config:
        from_attributes = True

class OrderItemSimple(BaseModel):
    """Упрощенная схема позиции заказа"""
    id: int
    product_id: int
    variant_id: Optional[int] = None
    quantity: int
    price: Decimal
    total: Decimal
    display_name: str
    
    class Config:
        from_attributes = True

class OrderItemWithProduct(OrderItemResponse):
    """Позиция заказа с информацией о товаре"""
    product: Optional['ProductSimple'] = None
    variant: Optional['ProductVariantSimple'] = None
    store: Optional['StoreSimple'] = None
    
    class Config:
        from_attributes = True

# === PAYMENT SCHEMAS ===

class PaymentBase(BaseModel):
    payment_method: PaymentMethod
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = "RUB"
    gateway: Optional[str] = None

class PaymentCreate(PaymentBase):
    """Схема для создания платежа"""
    order_id: int

class PaymentResponse(PaymentBase):
    """Схема для ответа с платежом"""
    id: int
    order_id: int
    status: PaymentStatus
    gateway_transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_successful: bool
    is_pending: bool
    
    class Config:
        from_attributes = True

class PaymentSimple(BaseModel):
    """Упрощенная схема платежа"""
    id: int
    payment_method: PaymentMethod
    amount: Decimal
    status: PaymentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentUpdate(BaseModel):
    """Обновление платежа"""
    status: PaymentStatus
    gateway_transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    processed_at: Optional[datetime] = None

# === SHIPPING SCHEMAS ===

class ShippingZoneBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    countries: Optional[List[str]] = None
    regions: Optional[List[str]] = None

class ShippingZoneCreate(ShippingZoneBase):
    """Схема для создания зоны доставки"""
    pass

class ShippingZoneUpdate(BaseModel):
    """Схема для обновления зоны доставки"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    countries: Optional[List[str]] = None
    regions: Optional[List[str]] = None

class ShippingZoneResponse(ShippingZoneBase):
    """Схема для ответа с зоной доставки"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ShippingZoneWithMethods(ShippingZoneResponse):
    """Зона доставки с методами"""
    shipping_methods: List['ShippingMethodResponse'] = []
    
    class Config:
        from_attributes = True

class ShippingMethodBase(BaseModel):
    zone_id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0, decimal_places=2)
    free_threshold: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    estimated_days: Optional[int] = Field(None, gt=0)

class ShippingMethodCreate(ShippingMethodBase):
    """Схема для создания метода доставки"""
    is_active: bool = True

class ShippingMethodUpdate(BaseModel):
    """Схема для обновления метода доставки"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    free_threshold: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    estimated_days: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

class ShippingMethodResponse(ShippingMethodBase):
    """Схема для ответа с методом доставки"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ShippingCalculation(BaseModel):
    """Расчет стоимости доставки"""
    method_id: int
    method_name: str
    price: Decimal
    is_free: bool
    estimated_days: Optional[int] = None
    free_threshold: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

# === ORDER SHIPMENT SCHEMAS ===

class OrderShipmentBase(BaseModel):
    order_id: int
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    tracking_url: Optional[str] = None

class OrderShipmentCreate(OrderShipmentBase):
    """Схема для создания отправки"""
    pass

class OrderShipmentUpdate(BaseModel):
    """Схема для обновления отправки"""
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    tracking_url: Optional[str] = None
    status: Optional[ShipmentStatus] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class OrderShipmentResponse(OrderShipmentBase):
    """Схема для ответа с отправкой"""
    id: int
    status: ShipmentStatus
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_trackable: bool
    estimated_delivery_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class OrderShipmentSimple(BaseModel):
    """Упрощенная схема отправки"""
    id: int
    tracking_number: Optional[str] = None
    status: ShipmentStatus
    shipped_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# === ORDER OPERATIONS SCHEMAS ===

class OrderCancel(BaseModel):
    """Схема для отмены заказа"""
    reason: str = Field(..., min_length=1, max_length=500)
    refund_amount: Optional[Decimal] = Field(None, ge=0)
    notify_customer: bool = True

class OrderRefund(BaseModel):
    """Схема для возврата заказа"""
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    reason: str = Field(..., min_length=1, max_length=500)
    refund_items: Optional[List[int]] = None  # ID позиций для возврата
    notify_customer: bool = True

class OrderConfirm(BaseModel):
    """Схема для подтверждения заказа"""
    estimated_delivery: Optional[datetime] = None
    notes: Optional[str] = None
    notify_customer: bool = True

class OrderShip(BaseModel):
    """Схема для отправки заказа"""
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    tracking_url: Optional[str] = None
    notify_customer: bool = True

# === ORDER ANALYTICS SCHEMAS ===

class OrderAnalytics(BaseModel):
    """Аналитика заказов"""
    total_orders: int
    total_revenue: Decimal
    avg_order_value: Decimal
    orders_by_status: Dict[str, int]
    orders_by_payment_status: Dict[str, int]
    conversion_rate: float  # Процент конверсии из корзины в заказ
    repeat_customer_rate: float
    
    class Config:
        from_attributes = True

class OrderMetrics(BaseModel):
    """Метрики заказов за период"""
    period: str
    orders_count: int
    revenue: Decimal
    avg_order_value: Decimal
    completed_orders: int
    cancelled_orders: int
    refunded_orders: int
    
    class Config:
        from_attributes = True

class OrderTrends(BaseModel):
    """Тренды заказов"""
    daily_orders: List[Dict[str, Any]]  # [{"date": "2024-01-01", "orders": 15, "revenue": 25000}]
    growth_rate: float  # Рост в процентах
    seasonal_patterns: Dict[str, float]
    peak_hours: List[int]  # Часы пиковых заказов
    
    class Config:
        from_attributes = True

class CustomerOrderBehavior(BaseModel):
    """Поведение клиента в заказах"""
    user_id: int
    total_orders: int
    total_spent: Decimal
    avg_order_value: Decimal
    favorite_categories: List[str]
    repeat_purchase_rate: float
    last_order_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StoreOrderMetrics(BaseModel):
    """Метрики заказов магазина"""
    store_id: int
    store_name: str
    orders_count: int
    revenue: Decimal
    avg_order_value: Decimal
    fulfillment_rate: float  # Процент выполненных заказов
    avg_processing_time: float  # Среднее время обработки в часах
    
    class Config:
        from_attributes = True

# === ORDER REPORTS SCHEMAS ===

class OrderReport(BaseModel):
    """Отчет по заказам"""
    period_start: datetime
    period_end: datetime
    total_orders: int
    total_revenue: Decimal
    completed_orders: int
    cancelled_rate: float
    refund_rate: float
    avg_fulfillment_time: float
    top_products: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class PaymentReport(BaseModel):
    """Отчет по платежам"""
    period_start: datetime
    period_end: datetime
    total_payments: int
    successful_payments: int
    failed_payments: int
    success_rate: float
    total_amount: Decimal
    by_method: Dict[str, Dict[str, Any]]
    
    class Config:
        from_attributes = True

# === ORDER NOTIFICATIONS SCHEMAS ===

class OrderNotificationData(BaseModel):
    """Данные для уведомлений о заказе"""
    order_id: int
    order_number: str
    customer_email: str
    status: OrderStatus
    total_amount: Decimal
    tracking_number: Optional[str] = None

class OrderStatusNotification(BaseModel):
    """Уведомление об изменении статуса заказа"""
    order_id: int
    old_status: OrderStatus
    new_status: OrderStatus
    message: Optional[str] = None
    send_email: bool = True
    send_sms: bool = False

# Для обратной совместимости с импортами моделей
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserSimple
    from app.schemas.product import ProductSimple, ProductVariantSimple
    from app.schemas.store import StoreSimple