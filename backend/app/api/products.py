# app/api/products.py - Без админских функций
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import (
    ProductCreate, ProductResponse, ProductUpdate, ProductWithDetails,
    CategoryResponse
)
from app.core.auth_dependencies import get_current_user

router = APIRouter()

# Локальные функции для проверки ролей
def require_business_or_admin(current_user: User = Depends(get_current_user)):
    """Проверка для бизнес-пользователей или админов"""
    if current_user.role not in [UserRole.BUSINESS, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Business account or admin required."
        )
    return current_user

# КАТЕГОРИИ (просмотр доступен всем)

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Получить все категории (доступно всем)"""
    categories = db.query(Category).all()
    return categories

# ТОВАРЫ - УПРАВЛЕНИЕ СВОИМИ ТОВАРАМИ

@router.get("/my/products/stats")
async def get_my_products_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_or_admin)
):
    """Получить статистику товаров текущего пользователя"""
    total_products = db.query(Product).filter(Product.seller_id == current_user.id).count()
    active_products = db.query(Product).filter(
        Product.seller_id == current_user.id,
        Product.is_active == True
    ).count()
    inactive_products = db.query(Product).filter(
        Product.seller_id == current_user.id,
        Product.is_active == False
    ).count()
    
    # Подсчет общей стоимости товаров
    total_value = db.query(func.sum(Product.price * Product.stock_quantity)).filter(
        Product.seller_id == current_user.id,
        Product.is_active == True
    ).scalar() or 0
    
    return {
        "total_products": total_products,
        "active_products": active_products,
        "inactive_products": inactive_products,
        "total_inventory_value": round(total_value, 2),
        "user_id": current_user.id,
        "user_role": current_user.role
    }

@router.get("/my/products/inactive", response_model=List[ProductResponse])
async def get_my_inactive_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_or_admin)
):
    """Получить только деактивированные товары текущего пользователя"""
    products = db.query(Product).filter(
        Product.seller_id == current_user.id,
        Product.is_active == False
    ).all()
    return products

@router.get("/my/products", response_model=List[ProductResponse])
async def get_my_products(
    include_inactive: bool = Query(False, description="Включить деактивированные товары"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_or_admin)
):
    """Получить товары текущего пользователя"""
    query = db.query(Product).filter(Product.seller_id == current_user.id)
    
    # Если не нужны неактивные товары, фильтруем только активные
    if not include_inactive:
        query = query.filter(Product.is_active == True)
    
    products = query.all()
    return products

@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_or_admin)
):
    """Создать новый товар"""
    db_product = Product(
        **product.dict(),
        seller_id=current_user.id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# ТОВАРЫ - ПУБЛИЧНЫЙ ПРОСМОТР

@router.get("/", response_model=List[ProductWithDetails])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    """Получить список товаров с фильтрами (доступно всем)"""
    query = db.query(Product).options(
        joinedload(Product.seller),
        joinedload(Product.category)
    ).filter(Product.is_active == True)
    
    # Фильтры
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if search:
        query = query.filter(Product.title.ilike(f"%{search}%"))
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    products = query.offset(skip).limit(limit).all()
    
    # Преобразуем в правильный формат
    result = []
    for product in products:
        product_data = {
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "price": product.price,
            "stock_quantity": product.stock_quantity,
            "category_id": product.category_id,
            "images": product.images or [],
            "seller_id": product.seller_id,
            "is_active": product.is_active,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "seller": None,
            "category": None
        }
        
        # Добавляем информацию о продавце
        if product.seller:
            product_data["seller"] = {
                "id": product.seller.id,
                "first_name": product.seller.first_name,
                "last_name": product.seller.last_name,
                "email": product.seller.email
            }
        
        # Добавляем информацию о категории
        if product.category:
            product_data["category"] = {
                "id": product.category.id,
                "name": product.category.name,
                "description": product.category.description,
                "parent_id": product.category.parent_id
            }
        
        result.append(product_data)
    
    return result

@router.get("/{product_id}", response_model=ProductWithDetails)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Получить товар по ID (доступно всем)"""
    product = db.query(Product).options(
        joinedload(Product.seller),
        joinedload(Product.category)
    ).filter(Product.id == product_id, Product.is_active == True).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Формируем ответ вручную
    product_data = {
        "id": product.id,
        "title": product.title,
        "description": product.description,
        "price": product.price,
        "stock_quantity": product.stock_quantity,
        "category_id": product.category_id,
        "images": product.images or [],
        "seller_id": product.seller_id,
        "is_active": product.is_active,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "seller": None,
        "category": None
    }
    
    if product.seller:
        product_data["seller"] = {
            "id": product.seller.id,
            "first_name": product.seller.first_name,
            "last_name": product.seller.last_name,
            "email": product.seller.email
        }
    
    if product.category:
        product_data["category"] = {
            "id": product.category.id,
            "name": product.category.name,
            "description": product.category.description,
            "parent_id": product.category.parent_id
        }
    
    return product_data

# ТОВАРЫ - РЕДАКТИРОВАНИЕ

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_or_admin)
):
    """Обновить товар"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Проверяем права: владелец товара или админ
    if current_user.role != UserRole.ADMIN and product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this product"
        )
    
    # Обновляем только переданные поля
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_or_admin)
):
    """Полностью удалить товар из базы данных"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Проверяем права: владелец товара или админ
    if current_user.role != UserRole.ADMIN and product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this product"
        )
    
    # Полное удаление из базы данных
    db.delete(product)
    db.commit()
    
    return {
        "message": "Product permanently deleted from database",
        "deleted_product_id": product_id,
        "deleted_by": current_user.role
    }

@router.patch("/{product_id}/deactivate")
async def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_or_admin)
):
    """Деактивировать товар (скрыть из каталога, но сохранить в БД)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Проверяем права: владелец товара или админ
    if current_user.role != UserRole.ADMIN and product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to deactivate this product"
        )
    
    if not product.is_active:
        return {
            "message": "Product is already deactivated",
            "product_id": product_id,
            "is_active": False
        }
    
    # Мягкое удаление - помечаем как неактивный
    product.is_active = False
    db.commit()
    
    return {
        "message": "Product deactivated successfully",
        "product_id": product_id,
        "is_active": False,
        "deactivated_by": current_user.role
    }

@router.patch("/{product_id}/activate")
async def activate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business_or_admin)
):
    """Активировать товар (вернуть в каталог)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Проверяем права: владелец товара или админ
    if current_user.role != UserRole.ADMIN and product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to activate this product"
        )
    
    if product.is_active:
        return {
            "message": "Product is already active",
            "product_id": product_id,
            "is_active": True
        }
    
    # Активируем товар
    product.is_active = True
    db.commit()
    
    return {
        "message": "Product activated successfully", 
        "product_id": product_id,
        "is_active": True,
        "activated_by": current_user.role
    }