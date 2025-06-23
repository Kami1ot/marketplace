# app/core/permissions.py
from fastapi import Depends, HTTPException, status
from app.models.user import User, UserRole
from app.core.auth_dependencies import get_current_user

def require_role(required_role: UserRole):
    """Фабрика для создания зависимости проверки роли"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role == UserRole.ADMIN:
            # Админ может все
            return current_user
        
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        return current_user
    return role_checker

def require_business_or_admin(current_user: User = Depends(get_current_user)):
    """Проверка для бизнес-пользователей или админов"""
    if current_user.role not in [UserRole.BUSINESS, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Business account or admin required."
        )
    return current_user

def require_admin(current_user: User = Depends(get_current_user)):
    """Проверка только для админов"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user

# Алиасы для удобства
RequireUser = Depends(get_current_user)  # Любой авторизованный пользователь
RequireBusiness = Depends(require_business_or_admin)  # Бизнес или админ
RequireAdmin = Depends(require_admin)  # Только админ