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

class StoreResponse(StoreBase):
    """Схема для ответа с магазином"""
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
    """Упрощенная схема магазина"""
    id: int
    name: str
    slug: str
    logo_url: Optional[str] = None
    is_verified: bool
    
    class Config:
        from_attributes = True

# === STORE STATS SCHEMAS ===

class StoreStatsBase(BaseModel):
    total_products: int = 0
    active_products: int = 0
    total_orders: int = 0
    completed_orders: int = 0
    cancelled_orders: int = 0
    total_revenue: Decimal = Decimal("0.00")
    monthly_revenue: Decimal = Decimal("0.00")
    rating_avg: Decimal = Decimal("0.00")
    rating_count: int = 0
    followers_count: int = 0
    views_count: int = 0

class StoreStatsResponse(StoreStatsBase):
    """Схема для ответа со статистикой магазина"""
    store_id: int
    updated_at: datetime
    success_rate: float
    average_order_value: Decimal
    
    class Config:
        from_attributes = True

class StoreWithStats(StoreResponse):
    """Магазин со статистикой"""
    stats: Optional[StoreStatsResponse] = None
    
    class Config:
        from_attributes = True

class StoreWithOwner(StoreResponse):
    """Магазин с информацией о владельце"""
    owner: Optional['UserSimple'] = None
    
    class Config:
        from_attributes = True

class StoreWithProducts(StoreResponse):
    """Магазин с товарами"""
    products: List['ProductSimple'] = []
    
    class Config:
        from_attributes = True

class StoreFull(StoreResponse):
    """Полная информация о магазине"""
    stats: Optional[StoreStatsResponse] = None
    owner: Optional['UserSimple'] = None
    address: Optional['UserAddressResponse'] = None
    
    class Config:
        from_attributes = True

class StoreList(BaseModel):
    """Список магазинов с пагинацией"""
    stores: List[StoreResponse]
    total: int
    page: int
    size: int
    pages: int

class StoreFilter(BaseModel):
    """Фильтр магазинов"""
    status: Optional[StoreStatus] = None
    verification_status: Optional[VerificationStatus] = None
    business_type: Optional[BusinessType] = None
    owner_id: Optional[int] = None
    search: Optional[str] = None
    has_products: Optional[bool] = None

class StoreSort(str, Enum):
    """Сортировка магазинов"""
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    CREATED_ASC = "created_asc"
    CREATED_DESC = "created_desc"
    RATING_ASC = "rating_asc"
    RATING_DESC = "rating_desc"
    REVENUE_ASC = "revenue_asc"
    REVENUE_DESC = "revenue_desc"

# Для обратной совместимости с импортами
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserSimple
    from app.schemas.product import ProductSimple
    from app.schemas.user import UserAddressResponse