# app/api/v1/users.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import User, UserProfile, UserAddress
from app.schemas import (
    UserResponse, UserUpdate, UserWithProfile, UserWithAddresses,
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    UserAddressCreate, UserAddressUpdate, UserAddressResponse
)
from app.core.auth_dependencies import get_current_active_user, get_admin_user

router = APIRouter()

@router.get("/me", response_model=UserWithProfile)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Получить профиль текущего пользователя"""
    user = db.query(User).options(
        joinedload(User.profile)
    ).filter(User.id == current_user.id).first()
    return user

@router.put("/me", response_model=UserResponse)
def update_current_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Обновить профиль текущего пользователя"""
    # Обновляем данные
    update_data = user_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

# === ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ===

@router.post("/me/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
def create_user_profile(
    *,
    db: Session = Depends(get_db),
    profile_in: UserProfileCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Создать профиль пользователя"""
    # Проверяем, нет ли уже профиля
    if current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )
    
    profile = UserProfile(
        user_id=current_user.id,
        **profile_in.dict()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.put("/me/profile", response_model=UserProfileResponse)
def update_user_profile(
    *,
    db: Session = Depends(get_db),
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Обновить профиль пользователя"""
    if not current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    update_data = profile_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user.profile, field, value)
    
    db.commit()
    db.refresh(current_user.profile)
    return current_user.profile

# === АДРЕСА ПОЛЬЗОВАТЕЛЯ ===

@router.get("/me/addresses", response_model=List[UserAddressResponse])
def get_user_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> Any:
    """Получить адреса пользователя"""
    addresses = db.query(UserAddress).filter(
        UserAddress.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return addresses

@router.post("/me/addresses", response_model=UserAddressResponse, status_code=status.HTTP_201_CREATED)
def create_user_address(
    *,
    db: Session = Depends(get_db),
    address_in: UserAddressCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Создать адрес пользователя"""
    # Если это адрес по умолчанию, убираем флаг у других
    if address_in.is_default:
        db.query(UserAddress).filter(
            UserAddress.user_id == current_user.id
        ).update({"is_default": False})
    
    address = UserAddress(
        user_id=current_user.id,
        **address_in.dict()
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address

@router.put("/me/addresses/{address_id}", response_model=UserAddressResponse)
def update_user_address(
    *,
    db: Session = Depends(get_db),
    address_id: int,
    address_in: UserAddressUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Обновить адрес пользователя"""
    address = db.query(UserAddress).filter(
        UserAddress.id == address_id,
        UserAddress.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # Если устанавливаем как основной
    if address_in.is_default and not address.is_default:
        db.query(UserAddress).filter(
            UserAddress.user_id == current_user.id,
            UserAddress.id != address_id
        ).update({"is_default": False})
    
    update_data = address_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(address, field, value)
    
    db.commit()
    db.refresh(address)
    return address

@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_address(
    *,
    db: Session = Depends(get_db),
    address_id: int,
    current_user: User = Depends(get_current_active_user)
) -> None:
    """Удалить адрес пользователя"""
    address = db.query(UserAddress).filter(
        UserAddress.id == address_id,
        UserAddress.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    db.delete(address)
    db.commit()

# === АДМИНСКИЕ ФУНКЦИИ ===

@router.get("/", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_admin_user)
) -> Any:
    """Получить список всех пользователей (только для админа)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserWithProfile)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
) -> Any:
    """Получить пользователя по ID (только для админа)"""
    user = db.query(User).options(
        joinedload(User.profile),
        joinedload(User.addresses)
    ).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user