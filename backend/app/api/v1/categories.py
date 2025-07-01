# app/api/v1/categories.py - добавить в начало файла
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Category, User  # Добавить User
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTree
from app.core.auth_dependencies import get_admin_user

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])   # Не работает: ResponseValidationError
def get_categories(
    db: Session = Depends(get_db),
    only_root: bool = False,
    only_active: bool = True
) -> Any:
    """Получить список категорий"""
    query = db.query(Category)
    
    if only_root:
        query = query.filter(Category.parent_id == None)
    
    if only_active:
        query = query.filter(Category.is_active == True)
    
    query = query.order_by(Category.sort_order, Category.name)
    categories = query.all()
    
    return categories

@router.get("/tree", response_model=List[CategoryTree])
def get_categories_tree(
    db: Session = Depends(get_db)
) -> Any:
    """Получить дерево категорий"""
    # Получаем корневые категории с подкатегориями
    categories = db.query(Category).options(
        joinedload(Category.children)
    ).filter(
        Category.parent_id == None,
        Category.is_active == True
    ).order_by(Category.sort_order, Category.name).all()
    
    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Получить категорию"""
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(get_admin_user)
) -> Any:
    """Создать категорию (только админ)"""
    # Проверяем уникальность slug
    if db.query(Category).filter(Category.slug == category_in.slug).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this slug already exists"
        )
    
    # Проверяем родительскую категорию
    if category_in.parent_id:
        parent = db.query(Category).filter(Category.id == category_in.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found"
            )
    
    category = Category(**category_in.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(get_admin_user)
) -> Any:
    """Обновить категорию (только админ)"""
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    update_data = category_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user: User = Depends(get_admin_user)
) -> None:
    """Удалить категорию (только админ)"""
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Проверяем, нет ли подкатегорий
    if category.children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with subcategories"
        )
    
    # Проверяем, нет ли товаров
    if category.products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with products"
        )
    
    db.delete(category)
    db.commit()