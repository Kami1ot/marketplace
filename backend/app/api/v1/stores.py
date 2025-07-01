# app/api/v1/stores.py
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.database import get_db
from app.models import Store, StoreStats, User, Product
from app.schemas import (
    StoreCreate, StoreUpdate, StoreResponse, StoreWithStats,
    StoreList, StoreFilter, ProductResponse
)
from app.core.auth_dependencies import get_current_active_user, get_seller_user, get_admin_user

router = APIRouter()

@router.get("/", response_model=StoreList)
def get_stores(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    verified_only: bool = False
) -> Any:
    """Получить список магазинов"""
    query = db.query(Store)
    
    # Фильтрация
    if status:
        query = query.filter(Store.status == status)
    else:
        query = query.filter(Store.status == "active")
    
    if verified_only:
        query = query.filter(Store.verification_status == "verified")
    
    if search:
        query = query.filter(
            Store.name.ilike(f"%{search}%")
        )
    
    total = query.count()
    stores = query.offset(skip).limit(limit).all()
    
    return {
        "stores": stores,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }

@router.get("/my", response_model=Optional[StoreWithStats])
def get_my_store(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
) -> Any:
    """Получить свой магазин"""
    store = db.query(Store).options(
        joinedload(Store.stats)
    ).filter(Store.owner_id == current_user.id).first()
    
    return store

@router.get("/{store_id}", response_model=StoreWithStats)
def get_store(
    store_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Получить информацию о магазине"""
    store = db.query(Store).options(
        joinedload(Store.stats),
        joinedload(Store.owner)
    ).filter(
        Store.id == store_id,
        Store.status == "active"
    ).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    return store

@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
def create_store(
    *,
    db: Session = Depends(get_db),
    store_in: StoreCreate,
    current_user: User = Depends(get_seller_user)
) -> Any:
    """Создать магазин"""
    # Проверяем, нет ли уже магазина у пользователя
    existing_store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    if existing_store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a store"
        )
    
    # Проверяем уникальность slug
    if db.query(Store).filter(Store.slug == store_in.slug).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Store with this slug already exists"
        )
    
    # Создаем магазин
    store = Store(
        **store_in.dict(exclude={"owner_id"}),
        owner_id=current_user.id
    )
    db.add(store)
    db.flush()
    
    # Создаем статистику для магазина
    stats = StoreStats(store_id=store.id)
    db.add(stats)
    
    db.commit()
    db.refresh(store)
    
    return store

@router.put("/{store_id}", response_model=StoreResponse)
def update_store(
    *,
    db: Session = Depends(get_db),
    store_id: int,
    store_in: StoreUpdate,
    current_user: User = Depends(get_seller_user)
) -> Any:
    """Обновить магазин"""
    store = db.query(Store).filter(Store.id == store_id).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Проверяем права
    if store.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Обновляем данные
    update_data = store_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(store, field, value)
    
    db.commit()
    db.refresh(store)
    return store

@router.get("/{store_id}/products", response_model=List[ProductResponse])
def get_store_products(
    store_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """Получить товары магазина"""
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.status == "active"
    ).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    products = db.query(Product).filter(
        Product.store_id == store_id,
        Product.status == "active"
    ).offset(skip).limit(limit).all()
    
    return products