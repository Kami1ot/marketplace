# app/models/attribute.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Enum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class AttributeType(str, enum.Enum):
    TEXT = "text"              # Текстовое поле
    NUMBER = "number"          # Число
    SELECT = "select"          # Выбор из списка
    MULTISELECT = "multiselect"  # Множественный выбор
    BOOLEAN = "boolean"        # Да/Нет
    COLOR = "color"           # Цвет с кодом
    SIZE = "size"             # Размер

class AttributeDefinition(Base):
    """Определение атрибута"""
    __tablename__ = "attribute_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)  # "size", "color", "material"
    name = Column(String(200), nullable=False)  # "Размер", "Цвет", "Материал"
    type = Column(Enum(AttributeType), nullable=False)
    unit = Column(String(50), nullable=True)  # "см", "кг", etc
    is_required = Column(Boolean, default=False)
    is_filter = Column(Boolean, default=True)  # Можно ли фильтровать
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Отношения
    category_attributes = relationship("CategoryAttribute", back_populates="attribute")
    attribute_values = relationship("AttributeValue", back_populates="attribute", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AttributeDefinition(code='{self.code}', name='{self.name}')>"


class AttributeValue(Base):
    """Возможные значения атрибута"""
    __tablename__ = "attribute_values"
    
    id = Column(Integer, primary_key=True, index=True)
    attribute_id = Column(Integer, ForeignKey("attribute_definitions.id"), nullable=False, index=True)
    value = Column(String(200), nullable=False)  # "XS", "Красный"
    display_name = Column(String(200), nullable=False)  # "Extra Small", "Красный цвет"
    meta_data = Column(JSON, nullable=True)  # {"color_code": "#FF0000", "size_chart": {...}}
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Отношения
    attribute = relationship("AttributeDefinition", back_populates="attribute_values")
    product_attributes = relationship("ProductAttribute", back_populates="attribute_value")
    
    # Уникальность значения в рамках атрибута
    __table_args__ = (
        UniqueConstraint('attribute_id', 'value', name='unique_attribute_value'),
    )
    
    def __repr__(self):
        return f"<AttributeValue(attribute_id={self.attribute_id}, value='{self.value}')>"


class CategoryAttribute(Base):
    """Связь категорий с атрибутами"""
    __tablename__ = "category_attributes"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    attribute_id = Column(Integer, ForeignKey("attribute_definitions.id"), nullable=False, index=True)
    is_required = Column(Boolean, default=False)  # Обязателен ли для этой категории
    is_variant = Column(Boolean, default=False)  # Создает ли варианты товара
    sort_order = Column(Integer, default=0)
    
    # Отношения
    category = relationship("Category", back_populates="category_attributes")
    attribute = relationship("AttributeDefinition", back_populates="category_attributes")
    
    # Уникальность
    __table_args__ = (
        UniqueConstraint('category_id', 'attribute_id', name='unique_category_attribute'),
    )
    
    def __repr__(self):
        return f"<CategoryAttribute(category_id={self.category_id}, attribute_id={self.attribute_id})>"


class ProductAttribute(Base):
    """Значения атрибутов для конкретного товара"""
    __tablename__ = "product_attributes"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True, index=True)
    attribute_id = Column(Integer, ForeignKey("attribute_definitions.id"), nullable=False, index=True)
    attribute_value_id = Column(Integer, ForeignKey("attribute_values.id"), nullable=True, index=True)
    custom_value = Column(Text, nullable=True)  # Для текстовых атрибутов
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    product = relationship("Product", back_populates="product_attributes")
    variant = relationship("ProductVariant", back_populates="product_attributes")
    attribute = relationship("AttributeDefinition")
    attribute_value = relationship("AttributeValue", back_populates="product_attributes")
    
    # Уникальность
    __table_args__ = (
        UniqueConstraint('product_id', 'variant_id', 'attribute_id', name='unique_product_attribute'),
    )
    
    def __repr__(self):
        return f"<ProductAttribute(product_id={self.product_id}, attribute_id={self.attribute_id})>"