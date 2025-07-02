# app/schemas/attribute.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AttributeType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    MULTISELECT = "multiselect"
    BOOLEAN = "boolean"
    COLOR = "color"
    SIZE = "size"

# === Attribute Definition Schemas ===

class AttributeDefinitionBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    type: AttributeType
    unit: Optional[str] = Field(None, max_length=50)
    is_required: bool = False
    is_filter: bool = True

class AttributeDefinitionCreate(AttributeDefinitionBase):
    """Создание определения атрибута"""
    sort_order: int = 0

class AttributeDefinitionUpdate(BaseModel):
    """Обновление определения атрибута"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    unit: Optional[str] = Field(None, max_length=50)
    is_required: Optional[bool] = None
    is_filter: Optional[bool] = None
    sort_order: Optional[int] = None

class AttributeDefinitionResponse(AttributeDefinitionBase):
    """Ответ с определением атрибута"""
    id: int
    sort_order: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# === Attribute Value Schemas ===

class AttributeValueBase(BaseModel):
    value: str = Field(..., min_length=1, max_length=200)
    display_name: str = Field(..., min_length=1, max_length=200)
    meta_data: Optional[Dict[str, Any]] = None

class AttributeValueCreate(AttributeValueBase):
    """Создание значения атрибута"""
    attribute_id: int
    sort_order: int = 0
    is_active: bool = True

class AttributeValueUpdate(BaseModel):
    """Обновление значения атрибута"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=200)
    meta_data: Optional[Dict[str, Any]] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class AttributeValueResponse(AttributeValueBase):
    """Ответ со значением атрибута"""
    id: int
    attribute_id: int
    sort_order: int
    is_active: bool
    
    class Config:
        from_attributes = True

# === Category Attribute Schemas ===

class CategoryAttributeBase(BaseModel):
    category_id: int
    attribute_id: int
    is_required: bool = False
    is_variant: bool = False

class CategoryAttributeCreate(CategoryAttributeBase):
    """Создание связи категории с атрибутом"""
    sort_order: int = 0

class CategoryAttributeUpdate(BaseModel):
    """Обновление связи категории с атрибутом"""
    is_required: Optional[bool] = None
    is_variant: Optional[bool] = None
    sort_order: Optional[int] = None

class CategoryAttributeResponse(CategoryAttributeBase):
    """Ответ со связью категории и атрибута"""
    id: int
    sort_order: int
    attribute: AttributeDefinitionResponse
    
    class Config:
        from_attributes = True

# === Product Attribute Schemas ===

class ProductAttributeBase(BaseModel):
    attribute_id: int
    attribute_value_id: Optional[int] = None
    custom_value: Optional[str] = None

class ProductAttributeCreate(ProductAttributeBase):
    """Создание атрибута товара"""
    product_id: int
    variant_id: Optional[int] = None

class ProductAttributeUpdate(BaseModel):
    """Обновление атрибута товара"""
    attribute_value_id: Optional[int] = None
    custom_value: Optional[str] = None

class ProductAttributeResponse(ProductAttributeBase):
    """Ответ с атрибутом товара"""
    id: int
    product_id: int
    variant_id: Optional[int] = None
    created_at: datetime
    attribute: AttributeDefinitionResponse
    attribute_value: Optional[AttributeValueResponse] = None
    
    class Config:
        from_attributes = True

# === Combined Schemas ===

class CategoryWithAttributes(BaseModel):
    """Категория с атрибутами"""
    id: int
    name: str
    attributes: List[CategoryAttributeResponse] = []
    
    class Config:
        from_attributes = True

class ProductWithAttributes(BaseModel):
    """Товар с атрибутами"""
    id: int
    name: str
    attributes: List[ProductAttributeResponse] = []
    
    class Config:
        from_attributes = True