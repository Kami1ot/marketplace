# app/init_db.py - обновленная версия
"""
Скрипт для инициализации базы данных
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import random

from app.database import engine, Base, SessionLocal
from app.models import *
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Инициализация базы данных"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tables created!")

def drop_db():
    """Удаление всех таблиц (осторожно!)"""
    logger.warning("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("✅ All tables dropped!")

def reset_db():
    """Полный сброс базы данных"""
    logger.warning("Resetting database...")
    
    # Удаляем все таблицы
    drop_db()
    
    # Создаем заново
    init_db()
    
    logger.info("✅ Database reset complete!")

def create_test_users(db: Session):
    """Создание тестовых пользователей"""
    logger.info("Creating test users...")
    
    users = [
        {
            "email": "admin@example.com",
            "password": "admin123",
            "first_name": "Admin",
            "last_name": "User",
            "role": UserRole.ADMIN,
            "email_verified": True
        },
        {
            "email": "seller@example.com", 
            "password": "seller123",
            "first_name": "Test",
            "last_name": "Seller",
            "role": UserRole.SELLER,
            "email_verified": True
        },
        {
            "email": "buyer@example.com",
            "password": "buyer123", 
            "first_name": "Test",
            "last_name": "Buyer",
            "role": UserRole.CUSTOMER,
            "email_verified": True
        }
    ]
    
    created_users = []
    for user_data in users:
        password = user_data.pop("password")
        user = User(**user_data)
        user.password_hash = get_password_hash(password)
        db.add(user)
        created_users.append(user)
        
        # Создаем профиль пользователя
        profile = UserProfile(
            user=user,
            bio=f"I am a {user.role.value}",
            language="ru"
        )
        db.add(profile)
        
        # Создаем адрес для покупателя
        if user.role == UserRole.CUSTOMER:
            address = UserAddress(
                user=user,
                type=AddressType.BOTH,
                label="Домашний адрес",
                country="Россия",
                city="Москва",
                street="ул. Тверская",
                building="1",
                postal_code="101000",
                is_default=True
            )
            db.add(address)
    
    db.commit()
    logger.info(f"✅ Created {len(created_users)} users")
    return created_users

def create_test_categories(db: Session):
    """Создание тестовых категорий"""
    logger.info("Creating test categories...")
    
    categories_data = [
        {"name": "Электроника", "slug": "electronics", "icon_url": "📱"},
        {"name": "Одежда и обувь", "slug": "clothing", "icon_url": "👕"},
        {"name": "Дом и сад", "slug": "home-garden", "icon_url": "🏠"},
        {"name": "Красота и здоровье", "slug": "beauty-health", "icon_url": "💄"},
        {"name": "Спорт и отдых", "slug": "sport", "icon_url": "⚽"},
        {"name": "Книги", "slug": "books", "icon_url": "📚"},
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category(**cat_data, is_active=True)
        db.add(category)
        categories.append(category)
    
    db.flush()  # Чтобы получить ID
    
    # Создаем подкатегории
    subcategories = [
        {"name": "Смартфоны", "slug": "smartphones", "parent_id": categories[0].id},
        {"name": "Ноутбуки", "slug": "laptops", "parent_id": categories[0].id},
        {"name": "Мужская одежда", "slug": "mens-clothing", "parent_id": categories[1].id},
        {"name": "Женская одежда", "slug": "womens-clothing", "parent_id": categories[1].id},
    ]
    
    for subcat_data in subcategories:
        subcategory = Category(**subcat_data, is_active=True)
        db.add(subcategory)
        categories.append(subcategory)
    
    db.commit()
    logger.info(f"✅ Created {len(categories)} categories")
    return categories

def create_test_brands(db: Session):
    """Создание тестовых брендов"""
    logger.info("Creating test brands...")
    
    brands_data = [
        {"name": "Apple", "slug": "apple", "website": "https://apple.com"},
        {"name": "Samsung", "slug": "samsung", "website": "https://samsung.com"},
        {"name": "Nike", "slug": "nike", "website": "https://nike.com"},
        {"name": "Adidas", "slug": "adidas", "website": "https://adidas.com"},
        {"name": "Sony", "slug": "sony", "website": "https://sony.com"},
    ]
    
    brands = []
    for brand_data in brands_data:
        brand = Brand(**brand_data, is_active=True)
        db.add(brand)
        brands.append(brand)
    
    db.commit()
    logger.info(f"✅ Created {len(brands)} brands")
    return brands

def seed_database():
    """Заполнение базы данных тестовыми данными"""
    db = SessionLocal()
    
    try:
        # Проверяем, пустая ли база
        if db.query(User).count() > 0:
            logger.warning("Database already contains data. Skipping seed.")
            return
        
        # Создаем тестовые данные
        users = create_test_users(db)
        categories = create_test_categories(db)
        brands = create_test_brands(db)
        
        logger.info("✅ Database seeded successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def check_enum_values():
    """Проверка значений enum"""
    logger.info("Checking enum values...")
    logger.info(f"UserRole values: {[role.value for role in UserRole]}")
    logger.info(f"UserStatus values: {[status.value for status in UserStatus]}")
    logger.info(f"AddressType values: {[addr_type.value for addr_type in AddressType]}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        # Полный сброс базы данных
        reset_db()
        seed_database()
    else:
        # Проверяем enum значения
        check_enum_values()
        
        # Создаем таблицы (если их еще нет)
        init_db()
        
        # Заполняем тестовыми данными
        seed_database()