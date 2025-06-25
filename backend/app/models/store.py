# app/models/store.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class StoreStatus(str, enum.Enum):
    ACTIVE = "active"        # Активный
    INACTIVE = "inactive"    # Неактивный  
    SUSPENDED = "suspended"  # Заблокированный

class VerificationStatus(str, enum.Enum):
    PENDING = "pending"      # На рассмотрении
    VERIFIED = "verified"    # Верифицирован
    REJECTED = "rejected"    # Отклонен

class BusinessType(str, enum.Enum):
    INDIVIDUAL = "individual"      # Физическое лицо
    COMPANY = "company"           # Компания
    ENTREPRENEUR = "entrepreneur"  # ИП

class Store(Base):
    __tablename__ = "stores"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Информация о магазине
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    banner_url = Column(Text, nullable=True)
    
    # Статусы
    status = Column(Enum(StoreStatus), default=StoreStatus.ACTIVE, nullable=False)
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    business_type = Column(Enum(BusinessType), nullable=True)
    
    # Бизнес информация
    tax_number = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    address_id = Column(Integer, ForeignKey("user_addresses.id"), nullable=True)
    
    # Настройки (JSON в виде текста)
    settings = Column(Text, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    owner = relationship("User", back_populates="stores")
    address = relationship("UserAddress", back_populates="stores")
    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")
    stats = relationship("StoreStats", back_populates="store", uselist=False, cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="store")
    conversations = relationship("Conversation", back_populates="store")
    
    def __repr__(self):
        return f"<Store(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def is_active(self):
        """Проверка, активен ли магазин"""
        return self.status == StoreStatus.ACTIVE
    
    @property
    def is_verified(self):
        """Проверка, верифицирован ли магазин"""
        return self.verification_status == VerificationStatus.VERIFIED
    
    @property
    def can_sell(self):
        """Может ли магазин продавать товары"""
        return self.is_active and self.is_verified
    
    @property
    def display_name(self):
        """Отображаемое имя магазина"""
        return self.name or f"Магазин {self.owner.full_name}"


class StoreStats(Base):
    __tablename__ = "store_stats"
    
    # Связь с магазином (PK и FK одновременно)
    store_id = Column(Integer, ForeignKey("stores.id"), primary_key=True, index=True)
    
    # Статистика товаров
    total_products = Column(Integer, default=0, nullable=False)
    active_products = Column(Integer, default=0, nullable=False)
    
    # Статистика заказов
    total_orders = Column(Integer, default=0, nullable=False)
    completed_orders = Column(Integer, default=0, nullable=False)
    cancelled_orders = Column(Integer, default=0, nullable=False)
    
    # Финансовая статистика
    total_revenue = Column(DECIMAL(15, 2), default=0, nullable=False)
    monthly_revenue = Column(DECIMAL(15, 2), default=0, nullable=False)
    
    # Рейтинги и отзывы
    rating_avg = Column(DECIMAL(3, 2), default=0, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)
    
    # Социальная статистика
    followers_count = Column(Integer, default=0, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    
    # Временная метка
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    store = relationship("Store", back_populates="stats")
    
    def __repr__(self):
        return f"<StoreStats(store_id={self.store_id}, products={self.total_products}, revenue={self.total_revenue})>"
    
    @property
    def success_rate(self):
        """Процент успешных заказов"""
        if self.total_orders == 0:
            return 0
        return round((self.completed_orders / self.total_orders) * 100, 1)
    
    @property
    def average_order_value(self):
        """Средний чек"""
        if self.completed_orders == 0:
            return 0
        return round(self.total_revenue / self.completed_orders, 2)