# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str

class UserCreateAdmin(UserBase):
    """Схема для создания пользователя админом (с выбором роли)"""
    password: str
    role: UserRole  # Админ может задать любую роль

class UserUpdateRole(BaseModel):
    """Схема для изменения роли пользователя"""
    role: UserRole

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None