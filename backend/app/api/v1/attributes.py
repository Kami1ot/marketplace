# app/api/v1/attributes.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AttributeDefinition, AttributeValue, CategoryAttribute, ProductAttribute, User
from app.schemas.attribute import (
    AttributeDefinitionCreate, AttributeDefinitionUpdate, AttributeDefinitionResponse,
    AttributeValueCreate, AttributeValueUpdate, AttributeValueResponse,
    CategoryAttributeCreate, CategoryAttributeResponse
)
from app.core.auth_dependencies import get_admin_user

router = APIRouter()

# === Attribute Definitions ===

@router.get("/definitions", response_model=List[AttributeDefinitionResponse])
def get_attribute_definitions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Получить все определения атрибутов"""
    attributes = db.query(AttributeDefinition).offset(skip).limit(limit).all()
    return attributes

@router.post("/definitions", response_model=AttributeDefinitionResponse)
def create_attribute_definition(
    *,
    db: Session = Depends(get_db),
    attribute_in: AttributeDefinitionCreate,
    current_user: User = Depends(get_admin_user)
) -> Any:
    """Создать определение атрибута (только админ)"""
    # Проверяем уникальность кода
    if db.query(AttributeDefinition).filter(AttributeDefinition.code == attribute_in.code).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attribute with this code already exists"
        )
    
    attribute = AttributeDefinition(**attribute_in.dict())
    db.add(attribute)
    db.commit()
    db.refresh(attribute)
    return attribute

# === Attribute Values ===

@router.get("/definitions/{attribute_id}/values", response_model=List[AttributeValueResponse])
def get_attribute_values(
    attribute_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Получить значения атрибута"""
    values = db.query(AttributeValue).filter(
        AttributeValue.attribute_id == attribute_id,
        AttributeValue.is_active == True
    ).order_by(AttributeValue.sort_order).all()
    return values

@router.post("/values", response_model=AttributeValueResponse)
def create_attribute_value(
    *,
    db: Session = Depends(get_db),
    value_in: AttributeValueCreate,
    current_user: User = Depends(get_admin_user)
) -> Any:
    """Создать значение атрибута (только админ)"""
    # Проверяем существование атрибута
    attribute = db.query(AttributeDefinition).filter(
        AttributeDefinition.id == value_in.attribute_id
    ).first()
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute definition not found"
        )
    
    # Проверяем уникальность значения
    existing = db.query(AttributeValue).filter(
        AttributeValue.attribute_id == value_in.attribute_id,
        AttributeValue.value == value_in.value
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Value already exists for this attribute"
        )
    
    value = AttributeValue(**value_in.dict())
    db.add(value)
    db.commit()
    db.refresh(value)
    return value

# === Category Attributes ===

@router.get("/categories/{category_id}/attributes", response_model=List[CategoryAttributeResponse])
def get_category_attributes(
    category_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Получить атрибуты категории"""
    attributes = db.query(CategoryAttribute).filter(
        CategoryAttribute.category_id == category_id
    ).order_by(CategoryAttribute.sort_order).all()
    return attributes

@router.post("/categories/{category_id}/attributes", response_model=CategoryAttributeResponse)
def assign_attribute_to_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    attribute_in: CategoryAttributeCreate,
    current_user: User = Depends(get_admin_user)
) -> Any:
    """Назначить атрибут категории (только админ)"""
    # Проверяем существование категории и атрибута
    # ... проверки ...
    
    # Проверяем, не назначен ли уже
    existing = db.query(CategoryAttribute).filter(
        CategoryAttribute.category_id == category_id,
        CategoryAttribute.attribute_id == attribute_in.attribute_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attribute already assigned to this category"
        )
    
    category_attr = CategoryAttribute(
        category_id=category_id,
        **attribute_in.dict()
    )
    db.add(category_attr)
    db.commit()
    db.refresh(category_attr)
    return category_attr