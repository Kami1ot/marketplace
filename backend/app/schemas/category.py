# app/schemas/category.py
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
    total_products_count: int
    full_path: str
    
    class Config:
        from_attributes = True

class CategorySimple(BaseModel):
    """Упрощенная схема категории для вложенных ответов"""
    id: int
    name: str
    slug: str
    image_url: Optional[str] = None
    icon_url: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True

class CategoryWithChildren(CategoryResponse):
    """Категория с дочерними категориями"""
    children: List['CategorySimple'] = []
    
    class Config:
        from_attributes = True

class CategoryWithParent(CategoryResponse):
    """Категория с родительской категорией"""
    parent: Optional[CategorySimple] = None
    
    class Config:
        from_attributes = True

class CategoryFull(CategoryResponse):
    """Полная информация о категории"""
    parent: Optional[CategorySimple] = None
    children: List[CategorySimple] = []
    
    class Config:
        from_attributes = True

class CategoryTree(BaseModel):
    """Дерево категорий"""
    id: int
    name: str
    slug: str
    image_url: Optional[str] = None
    icon_url: Optional[str] = None
    is_active: bool
    products_count: int
    children: List['CategoryTree'] = []
    
    class Config:
        from_attributes = True

class CategoryList(BaseModel):
    """Схема для списка категорий с пагинацией"""
    categories: List[CategoryResponse]
    total: int
    page: int
    size: int
    pages: int

class CategoryFilter(BaseModel):
    """Схема для фильтрации категорий"""
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_root: Optional[bool] = None  # Только корневые категории
    has_children: Optional[bool] = None  # Только категории с детьми
    search: Optional[str] = None  # Поиск по названию

class CategoryStats(BaseModel):
    """Статистика категории"""
    id: int
    name: str
    products_count: int
    total_products_count: int
    children_count: int
    level: int
    is_popular: bool  # Есть ли товары в наличии
    
    class Config:
        from_attributes = True

class CategoryBreadcrumb(BaseModel):
    """Хлебные крошки для категории"""
    id: int
    name: str
    slug: str
    
    class Config:
        from_attributes = True

class CategoryBreadcrumbs(BaseModel):
    """Список хлебных крошек"""
    breadcrumbs: List[CategoryBreadcrumb]
    current: CategoryBreadcrumb

class CategoryMove(BaseModel):
    """Схема для перемещения категории"""
    new_parent_id: Optional[int] = None
    new_sort_order: Optional[int] = None

class CategoryBulkUpdate(BaseModel):
    """Схема для массового обновления категорий"""
    category_ids: List[int]
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None

class CategoryImport(BaseModel):
    """Схема для импорта категорий"""
    name: str
    parent_name: Optional[str] = None  # Название родительской категории
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True

# Forward reference для избежания циклических импортов
CategoryWithChildren.model_rebuild()
CategoryTree.model_rebuild()