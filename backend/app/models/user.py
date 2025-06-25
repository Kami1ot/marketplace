# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Date, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"     # Покупатель
    SELLER = "seller"         # Продавец
    ADMIN = "admin"          # Администратор
    SUPPORT = "support"      # Поддержка

class UserStatus(str, enum.Enum):
    ACTIVE = "active"        # Активный
    INACTIVE = "inactive"    # Неактивный
    SUSPENDED = "suspended"  # Заблокированный
    DELETED = "deleted"      # Удаленный

class AddressType(str, enum.Enum):
    SHIPPING = "shipping"    # Адрес доставки
    BILLING = "billing"      # Адрес выставления счета
    BOTH = "both"           # Универсальный адрес

class User(Base):
    __tablename__ = "users"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    
    # Статусы и роли
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Верификация
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    deletion_requested_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Отношения
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
    stores = relationship("Store", back_populates="owner", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    wishlists = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    product_views = relationship("ProductView", back_populates="user")
    review_votes = relationship("ReviewVote", back_populates="user")
    discount_usages = relationship("DiscountUsage", back_populates="user")
    customer_conversations = relationship("Conversation", foreign_keys="Conversation.customer_id", back_populates="customer")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def full_name(self):
        """Полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.email.split('@')[0]
    
    @property
    def is_seller(self):
        """Проверка, является ли пользователь продавцом"""
        return self.role in [UserRole.SELLER, UserRole.ADMIN]
    
    @property
    def is_admin(self):
        """Проверка, является ли пользователь администратором"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_active_user(self):
        """Проверка, активен ли пользователь"""
        return self.status == UserStatus.ACTIVE and not self.deleted_at
    
    @property
    def default_address(self):
        """Получить адрес по умолчанию"""
        for address in self.addresses:
            if address.is_default:
                return address
        return self.addresses[0] if self.addresses else None


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    # Связь с пользователем (PK и FK одновременно)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    
    # Расширенная информация
    bio = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    social_links = Column(Text, nullable=True)  # JSON строка
    preferences = Column(Text, nullable=True)   # JSON строка для настроек
    timezone = Column(String(50), nullable=True)
    language = Column(String(10), default='ru', nullable=False)
    marketing_consent = Column(Boolean, default=False, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, language='{self.language}')>"


class UserAddress(Base):
    __tablename__ = "user_addresses"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Тип и метка адреса
    type = Column(Enum(AddressType), default=AddressType.SHIPPING, nullable=False)
    label = Column(String(100), nullable=True)  # "Дом", "Работа", "Дача"
    
    # Географическая информация
    country = Column(String(100), nullable=False)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=False)
    street = Column(String(255), nullable=False)
    building = Column(String(50), nullable=True)
    apartment = Column(String(50), nullable=True)
    postal_code = Column(String(20), nullable=True)
    coordinates = Column(String(100), nullable=True)  # "lat,lng"
    
    # Настройки
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    user = relationship("User", back_populates="addresses")
    stores = relationship("Store", back_populates="address")
    
    def __repr__(self):
        return f"<UserAddress(id={self.id}, city='{self.city}', type='{self.type}')>"
    
    @property
    def full_address(self):
        """Полный адрес в виде строки"""
        parts = [self.country, self.region, self.city, self.street]
        if self.building:
            parts.append(f"д. {self.building}")
        if self.apartment:
            parts.append(f"кв. {self.apartment}")
        return ", ".join(filter(None, parts))
    
    @property
    def short_address(self):
        """Краткий адрес"""
        parts = [self.city, self.street]
        if self.building:
            parts.append(f"д. {self.building}")
        return ", ".join(filter(None, parts))