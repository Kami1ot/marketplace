# app/schemas/brand.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

# === BRAND SCHEMAS ===

class BrandBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None

class BrandCreate(BrandBase):
    """Схема для создания нового бренда"""
    is_active: bool = True

class BrandUpdate(BaseModel):
    """Схема для обновления бренда"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None

class BrandResponse(BrandBase):
    """Схема для ответа с информацией о бренде"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    display_name: str
    has_logo: bool
    has_website: bool
    
    class Config:
        from_attributes = True

class BrandWithStats(BrandResponse):
    """Схема бренда с дополнительной статистикой"""
    products_count: int
    
    class Config:
        from_attributes = True

class BrandSimple(BaseModel):
    """Упрощенная схема бренда для вложенных ответов"""
    id: int
    name: str
    slug: str
    logo_url: Optional[str] = None
    display_name: str
    
    class Config:
        from_attributes = True

class BrandWithProducts(BrandResponse):
    """Бренд с товарами"""
    products_count: int  # Просто количество товаров
    
    class Config:
        from_attributes = True

class BrandStats(BaseModel):
    """Подробная статистика бренда"""
    id: int
    name: str
    products_count: int
    price_range: Optional[Dict[str, Decimal]] = None  # {"min": 100, "max": 5000, "count": 25}
    categories_count: int  # Количество категорий, в которых представлен бренд
    
    class Config:
        from_attributes = True

class BrandPopular(BaseModel):
    """Популярный бренд"""
    id: int
    name: str
    slug: str
    logo_url: Optional[str] = None
    products_count: int
    
    class Config:
        from_attributes = True

class BrandList(BaseModel):
    """Схема для списка брендов с пагинацией"""
    brands: List[BrandResponse]
    total: int
    page: int
    size: int
    pages: int

class BrandFilter(BaseModel):
    """Схема для фильтрации брендов"""
    is_active: Optional[bool] = None
    has_logo: Optional[bool] = None
    has_website: Optional[bool] = None
    has_products: Optional[bool] = None  # Только бренды с товарами
    category_id: Optional[int] = None  # Бренды в определенной категории
    search: Optional[str] = None  # Поиск по названию

class BrandSort(str, Enum):
    """Варианты сортировки брендов"""
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    PRODUCTS_COUNT_ASC = "products_asc"
    PRODUCTS_COUNT_DESC = "products_desc"
    CREATED_ASC = "created_asc"
    CREATED_DESC = "created_desc"

class BrandBulkUpdate(BaseModel):
    """Схема для массового обновления брендов"""
    brand_ids: List[int]
    is_active: Optional[bool] = None

class BrandImport(BaseModel):
    """Схема для импорта брендов"""
    name: str
    slug: Optional[str] = None  # Если не указан, генерируется автоматически
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True

class BrandExport(BaseModel):
    """Схема для экспорта бренда"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    is_active: bool
    products_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class BrandAnalytics(BaseModel):
    """Аналитика по бренду"""
    id: int
    name: str
    total_products: int
    active_products: int
    total_sales: Optional[Decimal] = None
    average_price: Optional[Decimal] = None
    price_range: Optional[Dict[str, Decimal]] = None
    top_categories: List[Dict[str, Any]] = []  # [{"category": "Electronics", "count": 15}]
    monthly_stats: List[Dict[str, Any]] = []  # Помесячная статистика
    
    class Config:
        from_attributes = True