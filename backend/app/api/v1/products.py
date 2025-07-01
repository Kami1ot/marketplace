# app/api/v1/products.py
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.database import get_db
from app.models import Product, ProductVariant, ProductImage, Category, Brand, Store, User  # Добавляем User!
from app.schemas import (
    ProductCreate, ProductUpdate, ProductResponse, ProductWithDetails,
    ProductVariantCreate, ProductVariantUpdate, ProductVariantResponse,
    ProductImageCreate, ProductImageResponse,
    ProductList, ProductFilter
)
from app.core.auth_dependencies import get_current_active_user, get_seller_user

router = APIRouter()

@router.get("/", response_model=ProductList)
def get_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    in_stock: Optional[bool] = None,
    sort_by: str = Query("created_desc", regex="^(price_asc|price_desc|name_asc|name_desc|created_asc|created_desc)$")
) -> Any:
    """Получить список товаров с фильтрацией"""
    query = db.query(Product).filter(
        Product.status == "active",
        Product.visibility == "published"
    )
    
    # Фильтрация
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    if in_stock is not None:
        if in_stock:
            query = query.filter(Product.stock_quantity > 0)
        else:
            query = query.filter(Product.stock_quantity == 0)
    
    # Подсчет общего количества
    total = query.count()
    
    # Сортировка
    sort_options = {
        "price_asc": Product.price.asc(),
        "price_desc": Product.price.desc(),
        "name_asc": Product.name.asc(),
        "name_desc": Product.name.desc(),
        "created_asc": Product.created_at.asc(),
        "created_desc": Product.created_at.desc()
    }
    query = query.order_by(sort_options[sort_by])
    
    # Пагинация
    products = query.offset(skip).limit(limit).all()
    
    return {
        "products": products,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }

@router.get("/{product_id}", response_model=ProductWithDetails)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Получить детальную информацию о товаре"""
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.brand),
        joinedload(Product.store),
        joinedload(Product.variants).joinedload(ProductVariant.images),
        joinedload(Product.images),
        joinedload(Product.reviews)
    ).filter(
        Product.id == product_id,
        Product.status == "active"
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
    current_user: User = Depends(get_seller_user)
) -> Any:
    """Создать новый товар (для продавцов)"""
    # Проверяем, есть ли у пользователя магазин
    store = db.query(Store).filter(
        Store.owner_id == current_user.id,
        Store.status == "active"
    ).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need an active store to create products"
        )
    
    # Проверяем уникальность SKU
    if db.query(Product).filter(Product.sku == product_in.sku).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    # Проверяем категорию и бренд
    if product_in.category_id:
        if not db.query(Category).filter(Category.id == product_in.category_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
    
    if product_in.brand_id:
        if not db.query(Brand).filter(Brand.id == product_in.brand_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand not found"
            )
    
    # Создаем товар
    product = Product(
        **product_in.dict(),
        store_id=store.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(get_seller_user)
) -> Any:
    """Обновить товар"""
    # Получаем товар
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Проверяем права (владелец магазина или админ)
    if current_user.role != "admin":
        store = db.query(Store).filter(
            Store.id == product.store_id,
            Store.owner_id == current_user.id
        ).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    # Обновляем данные
    update_data = product_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_seller_user)
) -> None:
    """Удалить товар (архивировать)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Проверяем права
    if current_user.role != "admin":
        store = db.query(Store).filter(
            Store.id == product.store_id,
            Store.owner_id == current_user.id
        ).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    # Архивируем товар вместо удаления
    product.status = "archived"
    db.commit()

# === ВАРИАНТЫ ТОВАРА ===

@router.post("/{product_id}/variants", response_model=ProductVariantResponse, status_code=status.HTTP_201_CREATED)
def create_product_variant(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    variant_in: ProductVariantCreate,
    current_user: User = Depends(get_seller_user)
) -> Any:
    """Создать вариант товара"""
    # Проверяем товар и права
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Проверяем права
    if current_user.role != "admin":
        store = db.query(Store).filter(
            Store.id == product.store_id,
            Store.owner_id == current_user.id
        ).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    # Проверяем уникальность SKU
    if db.query(ProductVariant).filter(ProductVariant.sku == variant_in.sku).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Variant with this SKU already exists"
        )
    
    # Создаем вариант
    variant = ProductVariant(
        product_id=product_id,
        **variant_in.dict()
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    
    return variant

# === ИЗОБРАЖЕНИЯ ТОВАРА ===

@router.post("/{product_id}/images", response_model=ProductImageResponse, status_code=status.HTTP_201_CREATED)
def create_product_image(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    image_in: ProductImageCreate,
    current_user: User = Depends(get_seller_user)
) -> Any:
    """Добавить изображение товара"""
    # Проверяем товар и права
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Проверяем права
    if current_user.role != "admin":
        store = db.query(Store).filter(
            Store.id == product.store_id,
            Store.owner_id == current_user.id
        ).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    # Если это главное изображение, убираем флаг у других
    if image_in.is_main:
        db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.variant_id == image_in.variant_id
        ).update({"is_main": False})
    
    # Создаем изображение
    image = ProductImage(
        product_id=product_id,
        **image_in.dict()
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    
    return image