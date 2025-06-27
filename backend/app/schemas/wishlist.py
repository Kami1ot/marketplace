# app/schemas/wishlist.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

# === ENUMS ===

class WishlistPrivacy(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    FRIENDS = "friends"

class WishlistSort(str, Enum):
    NEWEST = "newest"
    OLDEST = "oldest"
    PRICE_LOW = "price_low"
    PRICE_HIGH = "price_high"
    NAME = "name"
    AVAILABILITY = "availability"

class WishlistFilter(str, Enum):
    ALL = "all"
    AVAILABLE = "available"
    ON_SALE = "on_sale"
    OUT_OF_STOCK = "out_of_stock"
    PRICE_DROPPED = "price_dropped"

class StockStatus(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    UNAVAILABLE = "unavailable"

# === WISHLIST SCHEMAS ===

class WishlistBase(BaseModel):
    name: str = Field(default="Избранное", min_length=1, max_length=200)
    is_public: bool = False

class WishlistCreate(WishlistBase):
    """Схема для создания списка желаний"""
    is_default: bool = False

class WishlistUpdate(BaseModel):
    """Схема для обновления списка желаний"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    is_public: Optional[bool] = None

class WishlistResponse(WishlistBase):
    """Схема для ответа со списком желаний"""
    id: int
    user_id: int
    is_default: bool
    created_at: datetime
    updated_at: datetime
    total_items: int
    is_empty: bool
    total_value: Decimal
    
    class Config:
        from_attributes = True

class WishlistSimple(BaseModel):
    """Упрощенная схема списка желаний"""
    id: int
    name: str
    is_default: bool
    is_public: bool
    total_items: int
    
    class Config:
        from_attributes = True

class WishlistWithItems(WishlistResponse):
    """Список желаний с товарами"""
    items: List['WishlistItemResponse'] = []
    available_items_count: int
    
    class Config:
        from_attributes = True

class WishlistWithUser(WishlistResponse):
    """Список желаний с информацией о пользователе"""
    user: Optional['UserSimple'] = None
    
    class Config:
        from_attributes = True

class WishlistStats(BaseModel):
    """Статистика списка желаний"""
    total_items: int
    available_items: int
    unavailable_items: int
    items_on_sale: int
    total_value: Decimal
    average_item_price: Decimal
    price_range: Dict[str, Decimal]  # {"min": 100, "max": 5000}
    
    class Config:
        from_attributes = True

class WishlistSummary(BaseModel):
    """Сводка списков желаний пользователя"""
    total_wishlists: int
    total_items: int
    default_wishlist_id: int
    public_wishlists: int
    recent_additions: int  # За последнюю неделю
    
    class Config:
        from_attributes = True

class WishlistList(BaseModel):
    """Схема для списка желаний с пагинацией"""
    wishlists: List[WishlistResponse]
    total: int
    page: int
    size: int
    pages: int

class WishlistFilter(BaseModel):
    """Схема для фильтрации списков желаний"""
    user_id: Optional[int] = None
    is_public: Optional[bool] = None
    is_default: Optional[bool] = None
    is_empty: Optional[bool] = None
    search: Optional[str] = None  # Поиск по названию
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

# === WISHLIST ITEM SCHEMAS ===

class WishlistItemBase(BaseModel):
    product_id: int
    variant_id: Optional[int] = None

class WishlistItemCreate(WishlistItemBase):
    """Схема для добавления товара в список желаний"""
    wishlist_id: Optional[int] = None  # Если не указан, добавляется в дефолтный

class WishlistItemResponse(WishlistItemBase):
    """Схема для ответа с товаром из списка желаний"""
    id: int
    wishlist_id: int
    added_at: datetime
    current_price: Decimal
    compare_price: Optional[Decimal] = None
    is_available: bool
    is_on_sale: bool
    discount_percentage: int
    display_name: str
    image_url: Optional[str] = None
    stock_status: StockStatus
    
    class Config:
        from_attributes = True

class WishlistItemSimple(BaseModel):
    """Упрощенная схема товара из списка желаний"""
    id: int
    product_id: int
    variant_id: Optional[int] = None
    current_price: Decimal
    is_available: bool
    added_at: datetime
    
    class Config:
        from_attributes = True

class WishlistItemWithProduct(WishlistItemResponse):
    """Товар из списка желаний с информацией о продукте"""
    product: Optional['ProductSimple'] = None
    variant: Optional['ProductVariantSimple'] = None
    
    class Config:
        from_attributes = True

class WishlistItemWithWishlist(WishlistItemResponse):
    """Товар с информацией о списке желаний"""
    wishlist: Optional[WishlistSimple] = None
    
    class Config:
        from_attributes = True

class WishlistItemList(BaseModel):
    """Схема для списка товаров желаний с пагинацией"""
    items: List[WishlistItemResponse]
    total: int
    page: int
    size: int
    pages: int
    stats: Optional[WishlistStats] = None

class WishlistItemFilter(BaseModel):
    """Схема для фильтрации товаров в списке желаний"""
    wishlist_id: Optional[int] = None
    product_id: Optional[int] = None
    is_available: Optional[bool] = None
    is_on_sale: Optional[bool] = None
    stock_status: Optional[StockStatus] = None
    price_min: Optional[Decimal] = Field(None, ge=0)
    price_max: Optional[Decimal] = Field(None, ge=0)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None  # Поиск по названию товара

# === WISHLIST OPERATIONS SCHEMAS ===

class WishlistAddItem(BaseModel):
    """Схема для добавления товара в список желаний"""
    product_id: int
    variant_id: Optional[int] = None
    wishlist_id: Optional[int] = None  # Если не указан, добавляется в дефолтный

class WishlistRemoveItem(BaseModel):
    """Схема для удаления товара из списка желаний"""
    item_id: int

class WishlistMoveItem(BaseModel):
    """Схема для перемещения товара между списками"""
    item_id: int
    target_wishlist_id: int

class WishlistBulkAction(BaseModel):
    """Схема для массовых действий с товарами"""
    item_ids: List[int]
    action: str  # "remove", "move_to_cart", "move_to_wishlist"
    target_wishlist_id: Optional[int] = None  # Для action = "move_to_wishlist"

class WishlistMerge(BaseModel):
    """Схема для объединения списков желаний"""
    source_wishlist_id: int
    target_wishlist_id: int
    delete_source: bool = True

class WishlistShare(BaseModel):
    """Схема для шаринга списка желаний"""
    wishlist_id: int
    share_type: str  # "link", "email", "social"
    recipients: Optional[List[str]] = None  # Email адреса для share_type = "email"
    message: Optional[str] = None

# === WISHLIST ANALYTICS SCHEMAS ===

class WishlistAnalytics(BaseModel):
    """Аналитика списков желаний"""
    total_users_with_wishlists: int
    total_wishlists: int
    total_items: int
    avg_items_per_wishlist: float
    conversion_rate: float  # Процент товаров, купленных из списка желаний
    most_wishlisted_products: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class WishlistUserBehavior(BaseModel):
    """Поведение пользователя со списками желаний"""
    user_id: int
    total_wishlists: int
    total_items_added: int
    items_purchased: int
    conversion_rate: float
    avg_time_to_purchase: float  # В днях
    favorite_categories: List[str]
    
    class Config:
        from_attributes = True

class WishlistProductMetrics(BaseModel):
    """Метрики товара в списках желаний"""
    product_id: int
    times_wishlisted: int
    conversion_rate: float
    avg_time_in_wishlist: float  # В днях
    price_sensitivity: float  # Как цена влияет на добавление в список
    
    class Config:
        from_attributes = True

class WishlistTrends(BaseModel):
    """Тренды списков желаний"""
    period: str
    items_added: int
    items_removed: int
    items_purchased: int
    net_growth: int
    conversion_trend: float
    popular_categories: List[str]
    
    class Config:
        from_attributes = True

# === WISHLIST NOTIFICATIONS SCHEMAS ===

class WishlistNotification(BaseModel):
    """Уведомление о списке желаний"""
    type: str  # "price_drop", "back_in_stock", "limited_stock", "sale_started"
    wishlist_item_id: int
    user_id: int
    product_name: str
    message: str
    old_price: Optional[Decimal] = None
    new_price: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

class WishlistPriceAlert(BaseModel):
    """Оповещение о снижении цены"""
    wishlist_item_id: int
    user_id: int
    old_price: Decimal
    new_price: Decimal
    discount_percentage: float
    product_name: str
    
    class Config:
        from_attributes = True

class WishlistStockAlert(BaseModel):
    """Оповещение о поступлении товара"""
    wishlist_item_id: int
    user_id: int
    product_name: str
    current_stock: int
    back_in_stock_date: datetime
    
    class Config:
        from_attributes = True

# === WISHLIST RECOMMENDATIONS SCHEMAS ===

class WishlistRecommendation(BaseModel):
    """Рекомендации на основе списка желаний"""
    user_id: int
    recommended_products: List['ProductSimple']
    reason: str  # "similar_products", "frequently_bought_together", "price_match"
    confidence: float = Field(..., ge=0, le=1)
    
    class Config:
        from_attributes = True

class WishlistSimilarUsers(BaseModel):
    """Пользователи с похожими списками желаний"""
    user_id: int
    similar_users: List[Dict[str, Any]]  # [{"user_id": 123, "similarity": 0.85}]
    common_products: List[int]
    
    class Config:
        from_attributes = True

# === WISHLIST SHARING SCHEMAS ===

class WishlistPublic(BaseModel):
    """Публичный список желаний"""
    id: int
    name: str
    user_name: str
    user_avatar: Optional[str] = None
    total_items: int
    created_at: datetime
    preview_items: List[WishlistItemSimple]
    
    class Config:
        from_attributes = True

class WishlistShareLink(BaseModel):
    """Ссылка для шаринга списка желаний"""
    wishlist_id: int
    share_token: str
    expires_at: Optional[datetime] = None
    view_count: int = 0
    
    class Config:
        from_attributes = True

class WishlistGift(BaseModel):
    """Подарок из списка желаний"""
    wishlist_item_id: int
    gifter_id: int
    recipient_id: int
    message: Optional[str] = None
    is_anonymous: bool = False
    
    class Config:
        from_attributes = True

# === WISHLIST IMPORTS/EXPORTS SCHEMAS ===

class WishlistExport(BaseModel):
    """Экспорт списка желаний"""
    wishlist_id: int
    format: str = "csv"  # "csv", "xlsx", "json"
    include_prices: bool = True
    include_availability: bool = True
    include_images: bool = False

class WishlistImport(BaseModel):
    """Импорт товаров в список желаний"""
    wishlist_id: int
    file_url: str
    format: str  # "csv", "xlsx", "json"
    mapping: Dict[str, str]  # Маппинг полей файла к полям модели

# === WISHLIST WIDGETS SCHEMAS ===

class WishlistWidget(BaseModel):
    """Виджет списка желаний"""
    user_id: int
    total_items: int
    recent_items: List[WishlistItemSimple]
    items_on_sale: int
    total_savings: Decimal  # Общая экономия от скидок
    
    class Config:
        from_attributes = True

class WishlistButton(BaseModel):
    """Кнопка добавления в список желаний"""
    product_id: int
    variant_id: Optional[int] = None
    is_in_wishlist: bool
    wishlist_count: int  # Сколько раз товар добавлен в списки желаний всех пользователей
    
    class Config:
        from_attributes = True

# === WISHLIST COMPARISON SCHEMAS ===

class WishlistComparison(BaseModel):
    """Сравнение товаров из списка желаний"""
    wishlist_id: int
    item_ids: List[int]
    comparison_attributes: List[str]  # Атрибуты для сравнения
    
    class Config:
        from_attributes = True

class WishlistPriceHistory(BaseModel):
    """История цен товаров в списке желаний"""
    item_id: int
    price_history: List[Dict[str, Any]]  # [{"date": "2024-01-01", "price": 1000}]
    lowest_price: Decimal
    highest_price: Decimal
    current_trend: str  # "rising", "falling", "stable"
    
    class Config:
        from_attributes = True

# Для обратной совместимости с импортами моделей
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserSimple
    from app.schemas.product import ProductSimple, ProductVariantSimple