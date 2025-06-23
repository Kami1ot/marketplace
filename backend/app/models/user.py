# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "user"           # Обычный пользователь - только просмотр
    BUSINESS = "business"   # Бизнес - может продавать товары
    ADMIN = "admin"         # Администратор - полный доступ

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER)  # Новое поле роли
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Отношения
    products = relationship("Product", back_populates="seller")