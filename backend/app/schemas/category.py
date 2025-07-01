# app/schemas/category.py - обновленная версия
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# === CATEGORY SCHEMAS ===

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    icon_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    """Схема для создания категории"""
    slug: str = Field(..., min_length=1, max_length=200)
    sort_order: int = 0
    is_active: bool = True
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None

class CategoryUpdate(BaseModel):
    """Схема для обновления категории"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    icon_url: Optional[str] = None
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None

class CategoryResponse(CategoryBase):
    """Схема для ответа с категорией"""
    id: int
    slug: str
    sort_order: int
    is_active: bool
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_root_category: bool
    has_children: bool
    level: int
    products_count: int
    # Добавляем full_path
    full_path: str
    
    class Config:
        from_attributes = True

class CategorySimple(BaseModel):
    """Упрощенная схема категории"""
    id: int
    name: str
    slug: str
    icon_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class CategoryWithChildren(CategoryResponse):
    """Категория с подкатегориями"""
    children: List[CategorySimple] = []
    
    class Config:
        from_attributes = True

class CategoryWithProducts(CategoryResponse):
    """Категория с количеством товаров"""
    total_products_count: int
    
    class Config:
        from_attributes = True

class CategoryTree(CategoryResponse):
    """Дерево категорий"""
    children: List['CategoryTree'] = []
    
    class Config:
        from_attributes = True

class CategoryList(BaseModel):
    """Список категорий с пагинацией"""
    categories: List[CategoryResponse]
    total: int
    page: int
    size: int
    pages: int

class CategoryFilter(BaseModel):
    """Фильтр категорий"""
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None
    has_products: Optional[bool] = None
    search: Optional[str] = None

class CategorySort(str):
    """Сортировка категорий"""
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    SORT_ORDER = "sort_order"
    PRODUCTS_COUNT = "products_count"

class CategoryStats(BaseModel):
    """Статистика категории"""
    id: int
    name: str
    products_count: int
    active_products_count: int
    subcategories_count: int
    
    class Config:
        from_attributes = True

class CategoryAnalytics(BaseModel):
    """Аналитика категории"""
    id: int
    name: str
    views_count: int
    conversion_rate: float
    average_product_price: float
    top_selling_products: List[int]
    
    class Config:
        from_attributes = True

# Обновляем forward references
CategoryWithChildren.model_rebuild()
CategoryTree.model_rebuild()