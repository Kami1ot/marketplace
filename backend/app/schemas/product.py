# app/schemas/product.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Импортируем энумы из моделей
class ProductStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class ProductVisibility(str, Enum):
    PUBLISHED = "published"
    HIDDEN = "hidden"
    PASSWORD_PROTECTED = "password_protected"

# === PRODUCT SCHEMAS ===

class ProductBase(BaseModel):
    store_id: int
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=300)
    slug: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    compare_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    weight: Optional[Decimal] = Field(None, gt=0, decimal_places=3)
    dimensions: Optional[Dict[str, Any]] = None  # {"length": 10, "width": 5, "height": 2}

class ProductCreate(ProductBase):
    """Схема для создания товара"""
    status: ProductStatus = ProductStatus.DRAFT
    visibility: ProductVisibility = ProductVisibility.PUBLISHED
    track_inventory: bool = True
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)
    allow_backorder: bool = False
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None  # {"color": "red", "size": "XL"}
    tags: Optional[List[str]] = None  # ["новинка", "скидка", "хит"]

class ProductUpdate(BaseModel):
    """Схема для обновления товара"""
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    slug: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    compare_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    weight: Optional[Decimal] = Field(None, gt=0, decimal_places=3)
    dimensions: Optional[Dict[str, Any]] = None
    status: Optional[ProductStatus] = None
    visibility: Optional[ProductVisibility] = None
    track_inventory: Optional[bool] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    allow_backorder: Optional[bool] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class ProductResponse(ProductBase):
    """Схема для ответа с товаром"""
    id: int
    status: ProductStatus
    visibility: ProductVisibility
    track_inventory: bool
    stock_quantity: int
    low_stock_threshold: int
    allow_backorder: bool
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    is_published: bool
    is_in_stock: bool
    is_low_stock: bool
    discount_percentage: int
    effective_price: Decimal
    
    class Config:
        from_attributes = True

class ProductSimple(BaseModel):
    """Упрощенная схема товара для списков"""
    id: int
    name: str
    slug: str
    price: Decimal
    compare_price: Optional[Decimal] = None
    is_in_stock: bool
    discount_percentage: int
    
    class Config:
        from_attributes = True

# === PRODUCT VARIANT SCHEMAS ===

class ProductVariantBase(BaseModel):
    name: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    compare_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)
    weight: Optional[Decimal] = Field(None, gt=0, decimal_places=3)
    dimensions: Optional[Dict[str, Any]] = None
    attributes: Optional[Dict[str, Any]] = None  # {"color": "red", "size": "XL"}

class ProductVariantCreate(ProductVariantBase):
    """Схема для создания варианта товара"""
    product_id: int
    sort_order: int = 0
    is_active: bool = True

class ProductVariantUpdate(BaseModel):
    """Схема для обновления варианта товара"""
    name: Optional[str] = None
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    compare_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)
    weight: Optional[Decimal] = Field(None, gt=0, decimal_places=3)
    dimensions: Optional[Dict[str, Any]] = None
    attributes: Optional[Dict[str, Any]] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class ProductVariantResponse(ProductVariantBase):
    """Схема для ответа с вариантом товара"""
    id: int
    product_id: int
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    effective_price: Decimal
    effective_compare_price: Optional[Decimal] = None
    is_in_stock: bool
    is_low_stock: bool
    display_name: str
    discount_percentage: int
    
    class Config:
        from_attributes = True

class ProductVariantWithImages(ProductVariantResponse):
    """Вариант товара с изображениями"""
    images: List['ProductImageResponse'] = []
    
    class Config:
        from_attributes = True

# === PRODUCT IMAGE SCHEMAS ===

class ProductImageBase(BaseModel):
    url: str = Field(..., description="URL изображения")
    alt_text: Optional[str] = Field(None, max_length=255)

class ProductImageCreate(ProductImageBase):
    """Схема для создания изображения товара"""
    product_id: int
    variant_id: Optional[int] = None
    sort_order: int = 0
    is_main: bool = False

class ProductImageUpdate(BaseModel):
    """Схема для обновления изображения товара"""
    url: Optional[str] = None
    alt_text: Optional[str] = Field(None, max_length=255)
    sort_order: Optional[int] = None
    is_main: Optional[bool] = None

class ProductImageResponse(ProductImageBase):
    """Схема для ответа с изображением товара"""
    id: int
    product_id: int
    variant_id: Optional[int] = None
    sort_order: int
    is_main: bool
    created_at: datetime
    belongs_to_variant: bool
    belongs_to_product: bool
    effective_alt_text: str
    
    class Config:
        from_attributes = True

# === COMBINED SCHEMAS ===

class ProductWithDetails(ProductResponse):
    """Товар с полной информацией"""
    variants: List[ProductVariantWithImages] = []
    images: List[ProductImageResponse] = []
    main_image: Optional[ProductImageResponse] = None
    all_images: List[ProductImageResponse] = []
    price_range: Optional[Dict[str, Decimal]] = None
    
    class Config:
        from_attributes = True

class ProductWithVariants(ProductResponse):
    """Товар с вариантами"""
    variants: List[ProductVariantResponse] = []
    
    class Config:
        from_attributes = True

class ProductList(BaseModel):
    """Схема для списка товаров с пагинацией"""
    products: List[ProductSimple]
    total: int
    page: int
    size: int
    pages: int

class ProductFilter(BaseModel):
    """Схема для фильтрации товаров"""
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    store_id: Optional[int] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    status: Optional[ProductStatus] = None
    visibility: Optional[ProductVisibility] = None
    in_stock: Optional[bool] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None

class ProductSort(str, Enum):
    """Варианты сортировки товаров"""
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    CREATED_ASC = "created_asc"
    CREATED_DESC = "created_desc"
    POPULAR = "popular"
    RATING = "rating"

# Forward references для избежания циклических импортов
ProductVariantWithImages.model_rebuild()
ProductWithDetails.model_rebuild()