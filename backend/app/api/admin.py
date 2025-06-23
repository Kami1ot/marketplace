# app/api/admin.py - Новый файл для админских функций
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.category import Category
from app.schemas.user import UserCreate, UserResponse, UserCreateAdmin, UserUpdateRole
from app.schemas.product import CategoryCreate, CategoryResponse, ProductWithDetails
from app.core.security import get_password_hash
from app.core.auth_dependencies import get_current_user

router = APIRouter()

# Локальная функция для проверки админа
def require_admin_role(current_user: User = Depends(get_current_user)):
    """Проверка только для админов"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user

# УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ

@router.post("/users/create", response_model=UserResponse)
async def admin_create_user(
    user: UserCreateAdmin, 
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Создание пользователя админом (с выбором роли)"""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role  # Админ может установить любую роль
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/users/create-business", response_model=UserResponse)
async def admin_create_business_user(
    user: UserCreate, 
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Создание бизнес-пользователя админом"""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создаем бизнес-пользователя
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=UserRole.BUSINESS
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/users", response_model=List[UserResponse])
async def admin_get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Получить список всех пользователей"""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.patch("/users/{user_id}/promote-to-business", response_model=UserResponse)
async def admin_promote_user_to_business(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Повысить обычного пользователя до бизнес-аккаунта"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role == UserRole.BUSINESS:
        return {
            "message": "User is already a business account",
            "user": user
        }
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change admin role"
        )
    
    # Повышаем до бизнеса
    user.role = UserRole.BUSINESS
    db.commit()
    db.refresh(user)
    
    return user

@router.patch("/users/{user_id}/demote-to-user", response_model=UserResponse)
async def admin_demote_business_to_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Понизить бизнес-аккаунт до обычного пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role == UserRole.USER:
        return {
            "message": "User is already a regular user",
            "user": user
        }
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change admin role"
        )
    
    # Понижаем до обычного пользователя
    user.role = UserRole.USER
    
    # Деактивируем все товары пользователя
    products_deactivated = db.query(Product).filter(
        Product.seller_id == user.id,
        Product.is_active == True
    ).update({"is_active": False})
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User demoted to regular user",
        "user": user,
        "deactivated_products": products_deactivated
    }

@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def admin_change_user_role(
    user_id: int,
    role_update: UserUpdateRole,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Изменить роль пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_role = user.role
    user.role = role_update.role
    
    # Если понижаем с бизнеса до обычного пользователя, деактивируем товары
    if old_role == UserRole.BUSINESS and role_update.role == UserRole.USER:
        db.query(Product).filter(
            Product.seller_id == user.id,
            Product.is_active == True
        ).update({"is_active": False})
    
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Удалить пользователя и все его товары"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Нельзя удалить самого себя
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Подсчитываем товары
    products_count = db.query(Product).filter(Product.seller_id == user.id).count()
    
    # Удаляем товары пользователя
    db.query(Product).filter(Product.seller_id == user.id).delete()
    
    # Удаляем пользователя
    user_email = user.email
    db.delete(user)
    db.commit()
    
    return {
        "message": "User permanently deleted by admin",
        "deleted_user_id": user_id,
        "deleted_user_email": user_email,
        "deleted_products_count": products_count
    }

@router.patch("/users/{user_id}/deactivate")
async def admin_deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Деактивировать пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = False
    
    # Деактивируем товары пользователя
    products_updated = db.query(Product).filter(
        Product.seller_id == user.id,
        Product.is_active == True
    ).update({"is_active": False})
    
    db.commit()
    
    return {
        "message": "User deactivated by admin",
        "user_id": user_id,
        "deactivated_products_count": products_updated
    }

# УПРАВЛЕНИЕ ТОВАРАМИ

@router.get("/products", response_model=List[ProductWithDetails])
async def admin_get_all_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_inactive: bool = Query(False),
    seller_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Получить все товары включая неактивные"""
    query = db.query(Product).options(
        joinedload(Product.seller),
        joinedload(Product.category)
    )
    
    if not include_inactive:
        query = query.filter(Product.is_active == True)
    
    if seller_id:
        query = query.filter(Product.seller_id == seller_id)
    
    products = query.offset(skip).limit(limit).all()
    
    # Возвращаем полную информацию о товарах
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
        
        result.append(product_data)
    
    return result

# УПРАВЛЕНИЕ КАТЕГОРИЯМИ

@router.post("/categories", response_model=CategoryResponse)
async def admin_create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Создать новую категорию"""
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# СТАТИСТИКА И АНАЛИТИКА

@router.get("/stats")
async def admin_get_platform_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Получить общую статистику платформы"""
    
    # Статистика пользователей
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    business_users = db.query(User).filter(User.role == UserRole.BUSINESS).count()
    admin_users = db.query(User).filter(User.role == UserRole.ADMIN).count()
    
    # Статистика товаров
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Общая стоимость товаров
    total_value = db.query(func.sum(Product.price * Product.stock_quantity)).filter(
        Product.is_active == True
    ).scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users,
            "business": business_users,
            "admin": admin_users,
            "regular": total_users - business_users - admin_users
        },
        "products": {
            "total": total_products,
            "active": active_products,
            "inactive": total_products - active_products,
            "total_value": round(total_value, 2)
        }
    }