# app/schemas/product.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True

class SellerInfo(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    stock_quantity: int = 0
    category_id: Optional[int] = None
    images: Optional[List[str]] = []

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    seller_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductWithDetails(ProductResponse):
    seller: Optional[SellerInfo] = None
    category: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True