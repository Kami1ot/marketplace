# app/api/auth.py - Без админских функций
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.auth_dependencies import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя (только роль USER)"""
    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Принудительно устанавливаем роль USER для публичной регистрации
    if user.role != UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Public registration only allows USER role. Contact admin for business account."
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=UserRole.USER  # Принудительно USER
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Вход в систему"""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем, что аккаунт активен
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact support for reactivation."
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.email, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user

@router.get("/account-info")
async def get_account_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить подробную информацию об аккаунте и статистику"""
    
    # Подсчитываем товары
    from app.models.product import Product
    
    total_products = db.query(Product).filter(Product.seller_id == current_user.id).count()
    active_products = db.query(Product).filter(
        Product.seller_id == current_user.id,
        Product.is_active == True
    ).count()
    
    # Общая стоимость товаров
    total_value = db.query(func.sum(Product.price * Product.stock_quantity)).filter(
        Product.seller_id == current_user.id,
        Product.is_active == True
    ).scalar() or 0
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "products_stats": {
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": total_products - active_products,
            "total_inventory_value": round(total_value, 2)
        }
    }

@router.patch("/deactivate-account")
async def deactivate_user_account(
    password: str = Body(..., description="Пароль для подтверждения деактивации"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Деактивировать собственный аккаунт"""
    
    # Проверяем пароль для подтверждения
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    if not current_user.is_active:
        return {
            "message": "Account is already deactivated",
            "user_id": current_user.id,
            "is_active": False
        }
    
    # Деактивируем пользователя
    current_user.is_active = False
    
    # Деактивируем все товары пользователя
    from app.models.product import Product
    products_updated = db.query(Product).filter(
        Product.seller_id == current_user.id,
        Product.is_active == True
    ).update({"is_active": False})
    
    db.commit()
    
    return {
        "message": "Account deactivated successfully",
        "user_id": current_user.id,
        "is_active": False,
        "deactivated_products_count": products_updated,
        "note": "Account can be reactivated by contacting support"
    }

@router.post("/reactivate-account")
async def reactivate_account_with_credentials(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """Реактивировать деактивированный аккаунт"""
    
    # Находим пользователя (включая неактивных)
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Проверяем пароль
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    if user.is_active:
        return {
            "message": "Account is already active",
            "user_id": user.id,
            "is_active": True
        }
    
    # Реактивируем пользователя
    user.is_active = True
    db.commit()
    
    return {
        "message": "Account reactivated successfully",
        "user_id": user.id,
        "is_active": True,
        "note": "Products remain deactivated. Activate them manually if needed."
    }

@router.delete("/delete-account")
async def delete_user_account(
    password: str = Body(..., description="Пароль для подтверждения удаления"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Полностью удалить собственный аккаунт и все товары"""
    
    # Проверяем пароль для подтверждения
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Подсчитываем что будет удалено
    from app.models.product import Product
    products_count = db.query(Product).filter(Product.seller_id == current_user.id).count()
    
    # Удаляем все товары пользователя
    db.query(Product).filter(Product.seller_id == current_user.id).delete()
    
    # Удаляем самого пользователя
    user_email = current_user.email
    user_id = current_user.id
    db.delete(current_user)
    db.commit()
    
    return {
        "message": "User account permanently deleted",
        "deleted_user_id": user_id,
        "deleted_user_email": user_email,
        "deleted_products_count": products_count,
        "status": "success"
    }