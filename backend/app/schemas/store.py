# app/schemas/store.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Импортируем энумы из моделей
class StoreStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class BusinessType(str, Enum):
    INDIVIDUAL = "individual"
    COMPANY = "company"
    ENTREPRENEUR = "entrepreneur"

# === STORE SCHEMAS ===

class StoreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None

class StoreCreate(StoreBase):
    """Схема для создания магазина"""
    owner_id: int
    business_type: Optional[BusinessType] = None
    tax_number: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    address_id: Optional[int] = None
    settings: Optional[str] = None  # JSON строка

class StoreUpdate(BaseModel):
    """Схема для обновления магазина"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    business_type: Optional[BusinessType] = None
    tax_number: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    address_id: Optional[int] = None
    settings: Optional[str] = None

class StoreUpdateStatus(BaseModel):
    """Схема для обновления статуса магазина"""
    status: StoreStatus

class StoreUpdateVerification(BaseModel):
    """Схема для обновления статуса верификации"""
    verification_status: VerificationStatus
    verification_notes: Optional[str] = None

class StoreResponse(StoreBase):
    """Схема для ответа с информацией о магазине"""
    id: int
    owner_id: int
    status: StoreStatus
    verification_status: VerificationStatus
    business_type: Optional[BusinessType] = None
    tax_number: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address_id: Optional[int] = None
    settings: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_verified: bool
    can_sell: bool
    display_name: str
    
    class Config:
        from_attributes = True

class StoreSimple(BaseModel):
    """Упрощенная схема магазина для вложенных ответов"""
    id: int
    name: str
    slug: str
    logo_url: Optional[str] = None
    status: StoreStatus
    verification_status: VerificationStatus
    display_name: str
    
    class Config:
        from_attributes = True

class StoreWithStats(StoreResponse):
    """Магазин со статистикой"""
    stats: Optional['StoreStatsResponse'] = None
    
    class Config:
        from_attributes = True

class StoreWithOwner(StoreResponse):
    """Магазин с информацией о владельце"""
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    
    class Config:
        from_attributes = True

# === STORE STATS SCHEMAS ===

class StoreStatsBase(BaseModel):
    total_products: int = 0
    active_products: int = 0
    total_orders: int = 0
    total_revenue: Decimal = Decimal('0.00')
    average_rating: Optional[Decimal] = None
    total_reviews: int = 0

class StoreStatsCreate(StoreStatsBase):
    """Схема для создания статистики магазина"""
    store_id: int

class StoreStatsUpdate(BaseModel):
    """Схема для обновления статистики магазина"""
    total_products: Optional[int] = None
    active_products: Optional[int] = None
    total_orders: Optional[int] = None
    total_revenue: Optional[Decimal] = None
    average_rating: Optional[Decimal] = None
    total_reviews: Optional[int] = None

class StoreStatsResponse(StoreStatsBase):
    """Схема для ответа со статистикой магазина"""
    store_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# === COMBINED SCHEMAS ===

class StoreFull(StoreResponse):
    """Полная информация о магазине"""
    stats: Optional[StoreStatsResponse] = None
    owner_name: Optional[str] = None
    products_count: int = 0
    orders_count: int = 0
    
    class Config:
        from_attributes = True

class StoreList(BaseModel):
    """Схема для списка магазинов с пагинацией"""
    stores: List[StoreResponse]
    total: int
    page: int
    size: int
    pages: int

class StoreFilter(BaseModel):
    """Схема для фильтрации магазинов"""
    status: Optional[StoreStatus] = None
    verification_status: Optional[VerificationStatus] = None
    business_type: Optional[BusinessType] = None
    owner_id: Optional[int] = None
    has_products: Optional[bool] = None
    has_orders: Optional[bool] = None
    search: Optional[str] = None

class StoreSort(str, Enum):
    """Варианты сортировки магазинов"""
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    CREATED_ASC = "created_asc"
    CREATED_DESC = "created_desc"
    PRODUCTS_COUNT_ASC = "products_asc"
    PRODUCTS_COUNT_DESC = "products_desc"
    REVENUE_ASC = "revenue_asc"
    REVENUE_DESC = "revenue_desc"
    RATING_ASC = "rating_asc"
    RATING_DESC = "rating_desc"

class StoreAnalytics(BaseModel):
    """Аналитика магазина"""
    id: int
    name: str
    total_products: int
    active_products: int
    total_orders: int
    total_revenue: Decimal
    average_order_value: Optional[Decimal] = None
    conversion_rate: Optional[float] = None  # процент заказов от просмотров
    average_rating: Optional[Decimal] = None
    total_reviews: int
    monthly_revenue: List[Dict[str, Any]] = []  # Помесячная выручка
    top_products: List[Dict[str, Any]] = []  # Топ товары по продажам
    
    class Config:
        from_attributes = True

class StoreDashboard(BaseModel):
    """Дашборд магазина для владельца"""
    store: StoreResponse
    stats: StoreStatsResponse
    recent_orders_count: int
    pending_orders_count: int
    low_stock_products_count: int
    unread_messages_count: int
    today_revenue: Decimal
    month_revenue: Decimal
    
    class Config:
        from_attributes = True

class StoreVerificationRequest(BaseModel):
    """Запрос на верификацию магазина"""
    business_documents: List[str] = []  # URLs документов
    additional_info: Optional[str] = None

class StoreBulkUpdate(BaseModel):
    """Схема для массового обновления магазинов"""
    store_ids: List[int]
    status: Optional[StoreStatus] = None
    verification_status: Optional[VerificationStatus] = None

class StoreExport(BaseModel):
    """Схема для экспорта данных магазина"""
    id: int
    name: str
    slug: str
    owner_email: str
    status: StoreStatus
    verification_status: VerificationStatus
    business_type: Optional[BusinessType] = None
    total_products: int
    total_orders: int
    total_revenue: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True

# Forward reference для избежания циклических импортов
StoreWithStats.model_rebuild()