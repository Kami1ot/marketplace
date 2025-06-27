# app/schemas/analytics.py
from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# === ENUMS ===

class ViewerType(str, Enum):
    REGISTERED = "registered"
    GUEST = "guest"
    ANONYMOUS = "anonymous"

class BrowserType(str, Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"
    OTHER = "other"
    UNKNOWN = "unknown"

class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    UNKNOWN = "unknown"

class SearchResultType(str, Enum):
    SUCCESS = "success"
    NO_RESULTS = "no_results"
    ERROR = "error"

# === PRODUCT VIEW SCHEMAS ===

class ProductViewBase(BaseModel):
    product_id: int
    user_id: Optional[int] = None
    session_id: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    referrer: Optional[str] = None

class ProductViewCreate(ProductViewBase):
    """Схема для создания записи просмотра товара"""
    pass

class ProductViewResponse(ProductViewBase):
    """Схема для ответа с просмотром товара"""
    id: int
    viewed_at: datetime
    is_authenticated_view: bool
    hours_since_view: int
    is_recent_view: bool
    viewer_type: ViewerType
    is_mobile_view: bool
    browser_info: BrowserType
    
    class Config:
        from_attributes = True

class ProductViewSimple(BaseModel):
    """Упрощенная схема просмотра для аналитики"""
    id: int
    product_id: int
    user_id: Optional[int] = None
    viewed_at: datetime
    viewer_type: ViewerType
    is_mobile_view: bool
    
    class Config:
        from_attributes = True

class ProductViewWithProduct(ProductViewResponse):
    """Просмотр с информацией о товаре"""
    product: Optional['ProductSimple'] = None
    
    class Config:
        from_attributes = True

class ProductViewWithUser(ProductViewResponse):
    """Просмотр с информацией о пользователе"""
    user: Optional['UserSimple'] = None
    
    class Config:
        from_attributes = True

class ProductViewStats(BaseModel):
    """Статистика просмотров товара"""
    product_id: int
    total_views: int
    unique_users: int
    anonymous_views: int
    mobile_views: int
    recent_views: int  # За последние 24 часа
    avg_daily_views: float
    peak_hour: Optional[int] = None  # Час пик просмотров (0-23)
    
    class Config:
        from_attributes = True

class ProductViewList(BaseModel):
    """Схема для списка просмотров с пагинацией"""
    views: List[ProductViewResponse]
    total: int
    page: int
    size: int
    pages: int

class ProductViewFilter(BaseModel):
    """Схема для фильтрации просмотров товаров"""
    product_id: Optional[int] = None
    user_id: Optional[int] = None
    viewer_type: Optional[ViewerType] = None
    is_mobile: Optional[bool] = None
    browser: Optional[BrowserType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    is_recent: Optional[bool] = None  # Только недавние просмотры
    ip_address: Optional[str] = None

# === SEARCH LOG SCHEMAS ===

class SearchLogBase(BaseModel):
    user_id: Optional[int] = None
    session_id: Optional[str] = Field(None, max_length=255)
    query: str = Field(..., min_length=1, max_length=500)
    filters: Optional[Dict[str, Any]] = None
    results_count: Optional[int] = Field(None, ge=0)
    ip_address: Optional[str] = Field(None, max_length=45)

class SearchLogCreate(SearchLogBase):
    """Схема для создания записи поиска"""
    pass

class SearchLogResponse(SearchLogBase):
    """Схема для ответа с записью поиска"""
    id: int
    created_at: datetime
    is_authenticated_search: bool
    has_results: bool
    search_terms: List[str]
    search_length: int
    is_short_query: bool
    is_long_query: bool
    has_filters: bool
    filters_count: int
    is_successful_search: bool
    hours_since_search: int
    
    class Config:
        from_attributes = True

class SearchLogSimple(BaseModel):
    """Упрощенная схема поиска для аналитики"""
    id: int
    query: str
    results_count: Optional[int] = None
    created_at: datetime
    is_successful_search: bool
    
    class Config:
        from_attributes = True

class SearchLogWithUser(SearchLogResponse):
    """Поиск с информацией о пользователе"""
    user: Optional['UserSimple'] = None
    
    class Config:
        from_attributes = True

class SearchLogStats(BaseModel):
    """Статистика поисковых запросов"""
    total_searches: int
    unique_users: int
    successful_searches: int
    avg_results_per_search: float
    most_popular_terms: List[Dict[str, Any]]  # [{"term": "iphone", "count": 150}]
    empty_searches: int
    searches_with_filters: int
    avg_query_length: float
    
    class Config:
        from_attributes = True

class PopularSearchTerm(BaseModel):
    """Популярный поисковый термин"""
    term: str
    count: int
    success_rate: float  # Процент успешных поисков с этим термином
    avg_results: float
    
    class Config:
        from_attributes = True

class SearchLogList(BaseModel):
    """Схема для списка поисков с пагинацией"""
    searches: List[SearchLogResponse]
    total: int
    page: int
    size: int
    pages: int

class SearchLogFilter(BaseModel):
    """Схема для фильтрации поисковых запросов"""
    user_id: Optional[int] = None
    query: Optional[str] = None  # Поиск по содержанию запроса
    has_results: Optional[bool] = None
    has_filters: Optional[bool] = None
    is_short_query: Optional[bool] = None
    is_long_query: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_results: Optional[int] = Field(None, ge=0)
    max_results: Optional[int] = Field(None, ge=0)
    ip_address: Optional[str] = None

# === ANALYTICS AGGREGATION SCHEMAS ===

class DailyAnalytics(BaseModel):
    """Ежедневная аналитика"""
    date: datetime
    total_views: int
    unique_viewers: int
    total_searches: int
    unique_searchers: int
    successful_searches: int
    mobile_views_percent: float
    top_viewed_products: List[Dict[str, Any]]  # [{"product_id": 1, "views": 50}]
    top_search_terms: List[Dict[str, Any]]     # [{"term": "phone", "count": 20}]
    
    class Config:
        from_attributes = True

class HourlyAnalytics(BaseModel):
    """Почасовая аналитика"""
    hour: int = Field(..., ge=0, le=23)
    views_count: int
    searches_count: int
    unique_users: int
    
    class Config:
        from_attributes = True

class UserBehaviorAnalytics(BaseModel):
    """Аналитика поведения пользователя"""
    user_id: int
    total_views: int
    total_searches: int
    favorite_categories: List[str]
    search_patterns: List[str]
    device_preference: DeviceType
    active_hours: List[int]  # Часы активности
    last_activity: datetime
    
    class Config:
        from_attributes = True

class ProductAnalytics(BaseModel):
    """Аналитика товара"""
    product_id: int
    total_views: int
    unique_viewers: int
    conversion_rate: float  # Процент просмотров, приведших к покупке
    search_appearances: int  # Сколько раз товар появлялся в поиске
    avg_position_in_search: float  # Средняя позиция в результатах поиска
    bounce_rate: float  # Процент быстрых уходов
    view_duration: Optional[float] = None  # Среднее время просмотра (если отслеживается)
    
    class Config:
        from_attributes = True

class TrendingProduct(BaseModel):
    """Трендовый товар"""
    product_id: int
    current_views: int
    previous_views: int
    growth_rate: float  # Процент роста просмотров
    trend_score: float  # Комплексный показатель тренда
    
    class Config:
        from_attributes = True

class SearchTrend(BaseModel):
    """Тренд поисковых запросов"""
    term: str
    current_searches: int
    previous_searches: int
    growth_rate: float
    success_rate: float
    
    class Config:
        from_attributes = True

# === COMPARISON SCHEMAS ===

class AnalyticsComparison(BaseModel):
    """Сравнение аналитики за периоды"""
    current_period: DailyAnalytics
    previous_period: DailyAnalytics
    views_change: float  # Изменение в процентах
    searches_change: float
    users_change: float
    
    class Config:
        from_attributes = True

# Для обратной совместимости с импортами моделей
# (нужно для корректной работы forward references)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.product import ProductSimple
    from app.schemas.user import UserSimple