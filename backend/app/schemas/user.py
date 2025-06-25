# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

# Импортируем энумы из моделей
class UserRole(str, Enum):
    CUSTOMER = "customer"
    SELLER = "seller"
    ADMIN = "admin"
    SUPPORT = "support"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class AddressType(str, Enum):
    SHIPPING = "shipping"
    BILLING = "billing"
    BOTH = "both"

# === USER SCHEMAS ===

class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Пароль должен содержать минимум 6 символов")

class UserCreateAdmin(UserBase):
    """Схема для создания пользователя админом (с выбором роли)"""
    password: str = Field(..., min_length=6)
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE

class UserUpdate(BaseModel):
    """Схема для обновления профиля пользователя"""
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None

class UserUpdateRole(BaseModel):
    """Схема для изменения роли пользователя"""
    role: UserRole

class UserUpdateStatus(BaseModel):
    """Схема для изменения статуса пользователя"""
    status: UserStatus

class UserResponse(UserBase):
    id: int
    role: UserRole
    status: UserStatus
    email_verified: bool
    phone_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserWithProfile(UserResponse):
    """Пользователь с профилем"""
    profile: Optional['UserProfileResponse'] = None
    
    class Config:
        from_attributes = True

class UserSimple(BaseModel):
    """Упрощенная схема пользователя для вложенных ответов"""
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# === USER PROFILE SCHEMAS ===

class UserProfileBase(BaseModel):
    bio: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[str] = None  # JSON строка
    timezone: Optional[str] = None
    language: str = 'ru'
    marketing_consent: bool = False

class UserProfileCreate(UserProfileBase):
    """Схема для создания профиля пользователя"""
    pass

class UserProfileUpdate(BaseModel):
    """Схема для обновления профиля пользователя"""
    bio: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    marketing_consent: Optional[bool] = None

class UserProfileResponse(UserProfileBase):
    """Схема для ответа с профилем пользователя"""
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# === USER ADDRESS SCHEMAS ===

class UserAddressBase(BaseModel):
    type: AddressType = AddressType.SHIPPING
    label: Optional[str] = None
    country: str
    region: Optional[str] = None
    city: str
    street: str
    building: Optional[str] = None
    apartment: Optional[str] = None
    postal_code: Optional[str] = None
    coordinates: Optional[str] = None

class UserAddressCreate(UserAddressBase):
    """Схема для создания адреса"""
    is_default: bool = False

class UserAddressUpdate(BaseModel):
    """Схема для обновления адреса"""
    type: Optional[AddressType] = None
    label: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    postal_code: Optional[str] = None
    coordinates: Optional[str] = None
    is_default: Optional[bool] = None

class UserAddressResponse(UserAddressBase):
    """Схема для ответа с адресом"""
    id: int
    user_id: int
    is_default: bool
    created_at: datetime
    updated_at: datetime
    full_address: str
    short_address: str
    
    class Config:
        from_attributes = True

class UserWithAddresses(UserResponse):
    """Пользователь с адресами"""
    addresses: List[UserAddressResponse] = []
    default_address: Optional[UserAddressResponse] = None
    
    class Config:
        from_attributes = True

# === AUTH SCHEMAS ===

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class PasswordChange(BaseModel):
    """Схема для смены пароля"""
    current_password: str
    new_password: str = Field(..., min_length=6)

class PasswordReset(BaseModel):
    """Схема для сброса пароля"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Схема для подтверждения сброса пароля"""
    token: str
    new_password: str = Field(..., min_length=6)

# Forward reference для избежания циклических импортов
UserWithProfile.model_rebuild()