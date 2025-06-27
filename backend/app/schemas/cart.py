# app/schemas/cart.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

# === ENUMS ===

class CartStatus(str, Enum):
    ACTIVE = "active"
    ABANDONED = "abandoned"
    CONVERTED = "converted"
    EXPIRED = "expired"

class CartItemStatus(str, Enum):
    AVAILABLE = "available"
    PRICE_CHANGED = "price_changed"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    LOW_STOCK = "low_stock"

class CartAction(str, Enum):
    ADD = "add"
    UPDATE = "update"
    REMOVE = "remove"
    CLEAR = "clear"

# === CART SCHEMAS ===

class CartBase(BaseModel):
    user_id: Optional[int] = None
    session_id: Optional[str] = Field(None, max_length=255)
    expires_at: Optional[datetime] = None

class CartCreate(CartBase):
    """Схема для создания корзины"""
    pass

class CartUpdate(BaseModel):
    """Схема для обновления корзины"""
    expires_at: Optional[datetime] = None

class CartResponse(CartBase):
    """Схема для ответа с корзиной"""
    id: int
    created_at: datetime
    updated_at: datetime
    total_items: int
    total_amount: Decimal
    total_weight: Optional[Decimal] = None
    is_empty: bool
    
    class Config:
        from_attributes = True

class CartSimple(BaseModel):
    """Упрощенная схема корзины"""
    id: int
    total_items: int
    total_amount: Decimal
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CartWithItems(CartResponse):
    """Корзина с товарами"""
    items: List['CartItemResponse'] = []
    
    class Config:
        from_attributes = True

class CartWithUser(CartResponse):
    """Корзина с информацией о пользователе"""
    user: Optional['UserSimple'] = None
    
    class Config:
        from_attributes = True

class CartSummary(BaseModel):
    """Сводка корзины"""
    total_items: int
    total_amount: Decimal
    total_weight: Optional[Decimal] = None
    stores_count: int
    has_unavailable_items: bool
    has_price_changes: bool
    estimated_shipping: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

class CartStore(BaseModel):
    """Группировка товаров корзины по магазинам"""
    store: 'StoreSimple'
    items: List['CartItemResponse']
    items_count: int
    total_amount: Decimal
    total_weight: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

class CartWithStores(CartResponse):
    """Корзина, сгруппированная по магазинам"""
    stores: List[CartStore] = []
    
    class Config:
        from_attributes = True

class CartValidation(BaseModel):
    """Результат валидации корзины"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    unavailable_items: List[int] = []  # ID недоступных товаров
    price_changed_items: List[int] = []  # ID товаров с изменившейся ценой
    
    class Config:
        from_attributes = True

class CartList(BaseModel):
    """Схема для списка корзин с пагинацией"""
    carts: List[CartResponse]
    total: int
    page: int
    size: int
    pages: int

class CartFilter(BaseModel):
    """Схема для фильтрации корзин"""
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    status: Optional[CartStatus] = None
    is_empty: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_amount: Optional[Decimal] = Field(None, ge=0)
    max_amount: Optional[Decimal] = Field(None, ge=0)
    min_items: Optional[int] = Field(None, ge=0)
    max_items: Optional[int] = Field(None, ge=0)

# === CART ITEM SCHEMAS ===

class CartItemBase(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(..., gt=0)
    price: Decimal = Field(..., gt=0, decimal_places=2)

class CartItemCreate(BaseModel):
    """Схема для добавления товара в корзину"""
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(..., gt=0)

class CartItemUpdate(BaseModel):
    """Схема для обновления товара в корзине"""
    quantity: int = Field(..., gt=0)

class CartItemResponse(CartItemBase):
    """Схема для ответа с товаром корзины"""
    id: int
    cart_id: int
    created_at: datetime
    updated_at: datetime
    total_price: Decimal
    current_price: Decimal
    price_changed: bool
    is_available: bool
    stock_available: Optional[int] = None
    can_fulfill_quantity: bool
    display_name: str
    image_url: Optional[str] = None
    status: CartItemStatus
    
    class Config:
        from_attributes = True

class CartItemSimple(BaseModel):
    """Упрощенная схема товара корзины"""
    id: int
    product_id: int
    variant_id: Optional[int] = None
    quantity: int
    price: Decimal
    total_price: Decimal
    is_available: bool
    
    class Config:
        from_attributes = True

class CartItemWithProduct(CartItemResponse):
    """Товар корзины с информацией о продукте"""
    product: Optional['ProductSimple'] = None
    variant: Optional['ProductVariantSimple'] = None
    
    class Config:
        from_attributes = True

class CartItemWithCart(CartItemResponse):
    """Товар корзины с информацией о корзине"""
    cart: Optional[CartSimple] = None
    
    class Config:
        from_attributes = True

class CartItemList(BaseModel):
    """Схема для списка товаров корзины с пагинацией"""
    items: List[CartItemResponse]
    total: int
    page: int
    size: int
    pages: int

class CartItemFilter(BaseModel):
    """Схема для фильтрации товаров корзины"""
    cart_id: Optional[int] = None
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    status: Optional[CartItemStatus] = None
    is_available: Optional[bool] = None
    price_changed: Optional[bool] = None
    can_fulfill: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    min_quantity: Optional[int] = Field(None, ge=0)
    max_quantity: Optional[int] = Field(None, ge=0)

# === CART OPERATIONS SCHEMAS ===

class CartAddItem(BaseModel):
    """Схема для добавления товара в корзину"""
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(default=1, gt=0)

class CartUpdateItem(BaseModel):
    """Схема для обновления товара в корзине"""
    item_id: int
    quantity: int = Field(..., gt=0)

class CartRemoveItem(BaseModel):
    """Схема для удаления товара из корзины"""
    item_id: int

class CartBulkUpdate(BaseModel):
    """Схема для массового обновления корзины"""
    items: List[Dict[str, Any]]  # [{"item_id": 1, "quantity": 2}, {"item_id": 2, "quantity": 0}]

class CartMerge(BaseModel):
    """Схема для объединения корзин (например, при авторизации гостя)"""
    source_cart_id: Optional[int] = None
    source_session_id: Optional[str] = None
    target_cart_id: int

class CartTransfer(BaseModel):
    """Схема для переноса корзины между пользователями/сессиями"""
    target_user_id: Optional[int] = None
    target_session_id: Optional[str] = None

# === CART ANALYTICS SCHEMAS ===

class CartAnalytics(BaseModel):
    """Аналитика корзины"""
    total_carts: int
    active_carts: int
    abandoned_carts: int
    conversion_rate: float
    avg_cart_value: Decimal
    avg_items_per_cart: float
    most_added_products: List[Dict[str, Any]]
    most_removed_products: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class AbandonedCartAnalytics(BaseModel):
    """Аналитика брошенных корзин"""
    total_abandoned: int
    total_value_lost: Decimal
    avg_abandonment_time: float  # В часах
    top_abandonment_reasons: List[str]
    recovery_opportunities: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class CartConversionMetrics(BaseModel):
    """Метрики конверсии корзины"""
    period: str
    total_carts_created: int
    carts_with_purchases: int
    conversion_rate: float
    avg_time_to_purchase: float  # В часах
    bounce_rate: float  # Процент корзин с одним просмотром
    
    class Config:
        from_attributes = True

# === CART RECOMMENDATIONS SCHEMAS ===

class CartRecommendation(BaseModel):
    """Рекомендация для корзины"""
    type: str  # "frequently_bought_together", "similar_products", "upsell", "cross_sell"
    products: List['ProductSimple']
    reason: str
    confidence: float = Field(..., ge=0, le=1)
    
    class Config:
        from_attributes = True

class CartRecommendations(BaseModel):
    """Рекомендации для корзины"""
    cart_id: int
    recommendations: List[CartRecommendation]
    
    class Config:
        from_attributes = True

# === CART RECOVERY SCHEMAS ===

class CartRecoveryEmail(BaseModel):
    """Схема для email восстановления корзины"""
    cart_id: int
    email: str
    template: str
    discount_code: Optional[str] = None
    expires_at: Optional[datetime] = None

class CartRecoveryResult(BaseModel):
    """Результат попытки восстановления корзины"""
    cart_id: int
    recovered: bool
    recovery_value: Optional[Decimal] = None
    recovery_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Для обратной совместимости с импортами моделей
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserSimple
    from app.schemas.product import ProductSimple, ProductVariantSimple
    from app.schemas.store import StoreSimple