# app/api/v1/cart.py
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Cart, CartItem, Product, ProductVariant, User
from app.schemas import (
    CartResponse, CartWithItems, CartItemResponse,
    CartAddItem, CartUpdateItem
)
from app.core.auth_dependencies import get_current_user

router = APIRouter()

def get_or_create_cart(
    db: Session,
    user: Optional[User] = None,
    session_id: Optional[str] = None
) -> Cart:
    """Получить или создать корзину"""
    if user:
        # Для авторизованного пользователя
        cart = db.query(Cart).filter(Cart.user_id == user.id).first()
        if not cart:
            cart = Cart(user_id=user.id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
    else:
        # Для гостя
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session ID required for guest cart"
            )
        cart = db.query(Cart).filter(Cart.session_id == session_id).first()
        if not cart:
            cart = Cart(session_id=session_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
    
    return cart

@router.get("/", response_model=CartWithItems)
def get_cart(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    x_session_id: Optional[str] = Header(None)
) -> Any:
    """Получить корзину"""
    cart = get_or_create_cart(db, current_user, x_session_id)
    
    # Загружаем элементы корзины с товарами
    cart = db.query(Cart).options(
        joinedload(Cart.items).joinedload(CartItem.product),
        joinedload(Cart.items).joinedload(CartItem.variant)
    ).filter(Cart.id == cart.id).first()
    
    return cart

@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    *,
    db: Session = Depends(get_db),
    item_in: CartAddItem,
    current_user: Optional[User] = Depends(get_current_user),
    x_session_id: Optional[str] = Header(None)
) -> Any:
    """Добавить товар в корзину"""
    cart = get_or_create_cart(db, current_user, x_session_id)
    
    # Проверяем товар
    product = db.query(Product).filter(
        Product.id == item_in.product_id,
        Product.status == "active"
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Проверяем вариант, если указан
    variant = None
    if item_in.variant_id:
        variant = db.query(ProductVariant).filter(
            ProductVariant.id == item_in.variant_id,
            ProductVariant.product_id == item_in.product_id,
            ProductVariant.is_active == True
        ).first()
        
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product variant not found"
            )
    
    # Проверяем наличие на складе
    if product.track_inventory:
        stock = variant.stock_quantity if variant else product.stock_quantity
        if stock < item_in.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough stock"
            )
    
    # Проверяем, есть ли уже такой товар в корзине
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item_in.product_id,
        CartItem.variant_id == item_in.variant_id
    ).first()
    
    if existing_item:
        # Увеличиваем количество
        existing_item.quantity += item_in.quantity
        existing_item.price = variant.effective_price if variant else product.price
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Создаем новый элемент
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item_in.product_id,
            variant_id=item_in.variant_id,
            quantity=item_in.quantity,
            price=variant.effective_price if variant else product.price
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item

@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    item_in: CartUpdateItem,
    current_user: Optional[User] = Depends(get_current_user),
    x_session_id: Optional[str] = Header(None)
) -> Any:
    """Обновить количество товара в корзине"""
    cart = get_or_create_cart(db, current_user, x_session_id)
    
    # Получаем элемент корзины
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Проверяем наличие на складе
    product = cart_item.product
    if product.track_inventory:
        stock = cart_item.variant.stock_quantity if cart_item.variant else product.stock_quantity
        if stock < item_in.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough stock"
            )
    
    # Обновляем количество
    cart_item.quantity = item_in.quantity
    db.commit()
    db.refresh(cart_item)
    
    return cart_item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    x_session_id: Optional[str] = Header(None)
) -> None:
    """Удалить товар из корзины"""
    cart = get_or_create_cart(db, current_user, x_session_id)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    db.delete(cart_item)
    db.commit()

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    *,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    x_session_id: Optional[str] = Header(None)
) -> None:
    """Очистить корзину"""
    cart = get_or_create_cart(db, current_user, x_session_id)
    
    # Удаляем все элементы
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()