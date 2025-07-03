# app/init_db.py - обновленная версия
"""
Скрипт для инициализации базы данных
"""
import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import random

from app.database import engine, Base, SessionLocal
from app.models import *
from app.core.security import get_password_hash
from app.models import (
    Store, StoreStats, StoreStatus, VerificationStatus,
    AttributeDefinition, AttributeValue, AttributeType,
    CategoryAttribute, Product, ProductVariant, ProductAttribute,
    ProductStatus, ProductVisibility
)

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

def check_enum_values():
    """Проверка значений enum"""
    logger.info("Checking enum values...")
    logger.info(f"UserRole values: {[role.value for role in UserRole]}")
    logger.info(f"UserStatus values: {[status.value for status in UserStatus]}")
    logger.info(f"AddressType values: {[addr_type.value for addr_type in AddressType]}")

def create_test_stores(db: Session, users: List[User]):
    """Создание тестовых магазинов"""
    logger.info("Creating test stores...")
    
    # Находим админа и продавца
    admin = next((u for u in users if u.email == "admin@example.com"), None)
    seller = next((u for u in users if u.email == "seller@example.com"), None)
    
    if not admin:
        logger.warning("Admin user not found")
        return []
    
    stores = []
    
    # Создаем магазин для админа
    admin_store = Store(
        owner_id=admin.id,
        name="Official Store",
        slug="official-store",
        description="Официальный магазин маркетплейса",
        status=StoreStatus.ACTIVE,
        verification_status=VerificationStatus.VERIFIED,
        contact_email="store@example.com",
        contact_phone="+7 999 123-45-67"
    )
    db.add(admin_store)
    db.flush()
    
    # Создаем статистику для магазина
    admin_stats = StoreStats(store_id=admin_store.id)
    db.add(admin_stats)
    stores.append(admin_store)
    
    # Если есть продавец, создаем и его магазин
    if seller:
        seller_store = Store(
            owner_id=seller.id,
            name="Test Seller Store",
            slug="test-seller-store",
            description="Магазин тестового продавца",
            status=StoreStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED
        )
        db.add(seller_store)
        db.flush()
        
        seller_stats = StoreStats(store_id=seller_store.id)
        db.add(seller_stats)
        stores.append(seller_store)
    
    db.commit()
    logger.info(f"✅ Created {len(stores)} stores")
    return stores

def create_test_attributes(db: Session):
    """Создание тестовых атрибутов"""
    logger.info("Creating test attributes...")
    
    attributes = []
    
    # Размер для одежды
    size_attr = AttributeDefinition(
        code="clothing_size",
        name="Размер",
        type=AttributeType.SELECT,
        is_required=True,
        is_filter=True,
        sort_order=1
    )
    db.add(size_attr)
    db.flush()
    attributes.append(size_attr)
    
    # Значения размеров
    size_values = [
        {"value": "xs", "display_name": "XS", "meta_data": {"eu_size": "40-42", "chest_cm": "86-89"}},
        {"value": "s", "display_name": "S", "meta_data": {"eu_size": "44-46", "chest_cm": "90-93"}},
        {"value": "m", "display_name": "M", "meta_data": {"eu_size": "48-50", "chest_cm": "94-97"}},
        {"value": "l", "display_name": "L", "meta_data": {"eu_size": "52-54", "chest_cm": "98-101"}},
        {"value": "xl", "display_name": "XL", "meta_data": {"eu_size": "56-58", "chest_cm": "102-105"}},
        {"value": "xxl", "display_name": "XXL", "meta_data": {"eu_size": "60-62", "chest_cm": "106-109"}}
    ]
    
    for i, size_data in enumerate(size_values):
        size_value = AttributeValue(
            attribute_id=size_attr.id,
            value=size_data["value"],
            display_name=size_data["display_name"],
            meta_data=size_data["meta_data"],
            sort_order=i,
            is_active=True
        )
        db.add(size_value)
    
    # Цвет
    color_attr = AttributeDefinition(
        code="color",
        name="Цвет",
        type=AttributeType.COLOR,
        is_required=True,
        is_filter=True,
        sort_order=2
    )
    db.add(color_attr)
    db.flush()
    attributes.append(color_attr)
    
    # Значения цветов
    color_values = [
        {"value": "black", "display_name": "Черный", "meta_data": {"hex": "#000000", "rgb": "0,0,0"}},
        {"value": "white", "display_name": "Белый", "meta_data": {"hex": "#FFFFFF", "rgb": "255,255,255"}},
        {"value": "gray", "display_name": "Серый", "meta_data": {"hex": "#808080", "rgb": "128,128,128"}},
        {"value": "navy", "display_name": "Темно-синий", "meta_data": {"hex": "#000080", "rgb": "0,0,128"}},
        {"value": "red", "display_name": "Красный", "meta_data": {"hex": "#FF0000", "rgb": "255,0,0"}},
        {"value": "green", "display_name": "Зеленый", "meta_data": {"hex": "#00FF00", "rgb": "0,255,0"}}
    ]
    
    for i, color_data in enumerate(color_values):
        color_value = AttributeValue(
            attribute_id=color_attr.id,
            value=color_data["value"],
            display_name=color_data["display_name"],
            meta_data=color_data["meta_data"],
            sort_order=i,
            is_active=True
        )
        db.add(color_value)
    
    # Материал
    material_attr = AttributeDefinition(
        code="material",
        name="Материал",
        type=AttributeType.SELECT,
        is_required=False,
        is_filter=True,
        sort_order=3
    )
    db.add(material_attr)
    db.flush()
    attributes.append(material_attr)
    
    # Значения материалов
    material_values = [
        {"value": "cotton", "display_name": "Хлопок 100%"},
        {"value": "cotton_poly", "display_name": "Хлопок/Полиэстер"},
        {"value": "polyester", "display_name": "Полиэстер"},
        {"value": "linen", "display_name": "Лен"},
        {"value": "wool", "display_name": "Шерсть"}
    ]
    
    for i, material_data in enumerate(material_values):
        material_value = AttributeValue(
            attribute_id=material_attr.id,
            value=material_data["value"],
            display_name=material_data["display_name"],
            sort_order=i,
            is_active=True
        )
        db.add(material_value)
    
    # Пол
    gender_attr = AttributeDefinition(
        code="gender",
        name="Пол",
        type=AttributeType.SELECT,
        is_required=False,
        is_filter=True,
        sort_order=4
    )
    db.add(gender_attr)
    db.flush()
    attributes.append(gender_attr)
    
    gender_values = [
        {"value": "male", "display_name": "Мужской"},
        {"value": "female", "display_name": "Женский"},
        {"value": "unisex", "display_name": "Унисекс"}
    ]
    
    for i, gender_data in enumerate(gender_values):
        gender_value = AttributeValue(
            attribute_id=gender_attr.id,
            value=gender_data["value"],
            display_name=gender_data["display_name"],
            sort_order=i,
            is_active=True
        )
        db.add(gender_value)
    
    db.commit()
    logger.info(f"✅ Created {len(attributes)} attribute definitions")
    return attributes

def assign_attributes_to_categories(db: Session, categories: List[Category], attributes: List[AttributeDefinition]):
    """Назначение атрибутов категориям"""
    logger.info("Assigning attributes to categories...")
    
    # Находим категорию одежды
    clothing_category = next((c for c in categories if c.slug == "clothing"), None)
    if not clothing_category:
        logger.warning("Clothing category not found")
        return
    
    # Находим атрибуты
    size_attr = next((a for a in attributes if a.code == "clothing_size"), None)
    color_attr = next((a for a in attributes if a.code == "color"), None)
    material_attr = next((a for a in attributes if a.code == "material"), None)
    gender_attr = next((a for a in attributes if a.code == "gender"), None)
    
    # Назначаем атрибуты категории "Одежда и обувь"
    if size_attr:
        cat_attr = CategoryAttribute(
            category_id=clothing_category.id,
            attribute_id=size_attr.id,
            is_required=True,
            is_variant=True,  # Размер создает варианты
            sort_order=1
        )
        db.add(cat_attr)
    
    if color_attr:
        cat_attr = CategoryAttribute(
            category_id=clothing_category.id,
            attribute_id=color_attr.id,
            is_required=True,
            is_variant=True,  # Цвет тоже создает варианты
            sort_order=2
        )
        db.add(cat_attr)
    
    if material_attr:
        cat_attr = CategoryAttribute(
            category_id=clothing_category.id,
            attribute_id=material_attr.id,
            is_required=False,
            is_variant=False,  # Материал НЕ создает варианты
            sort_order=3
        )
        db.add(cat_attr)
    
    if gender_attr:
        cat_attr = CategoryAttribute(
            category_id=clothing_category.id,
            attribute_id=gender_attr.id,
            is_required=False,
            is_variant=False,  # Пол НЕ создает варианты
            sort_order=4
        )
        db.add(cat_attr)
    
    # Также назначаем подкатегориям
    subcategories = ["mens-clothing", "womens-clothing"]
    for subcat_slug in subcategories:
        subcat = next((c for c in categories if c.slug == subcat_slug), None)
        if subcat and size_attr and color_attr:
            # Размер
            db.add(CategoryAttribute(
                category_id=subcat.id,
                attribute_id=size_attr.id,
                is_required=True,
                is_variant=True,
                sort_order=1
            ))
            # Цвет
            db.add(CategoryAttribute(
                category_id=subcat.id,
                attribute_id=color_attr.id,
                is_required=True,
                is_variant=True,
                sort_order=2
            ))
    
    db.commit()
    logger.info("✅ Attributes assigned to categories")

def create_test_products(db: Session, stores: List[Store], categories: List[Category], brands: List[Brand]):
    """Создание тестовых товаров"""
    logger.info("Creating test products...")
    
    # Находим нужные объекты
    official_store = next((s for s in stores if s.slug == "official-store"), None)
    mens_clothing = next((c for c in categories if c.slug == "mens-clothing"), None)
    nike_brand = next((b for b in brands if b.slug == "nike"), None)
    
    if not official_store or not mens_clothing or not nike_brand:
        logger.warning("Required objects not found for product creation")
        return []
    
    # Получаем атрибуты и их значения
    size_attr = db.query(AttributeDefinition).filter_by(code="clothing_size").first()
    color_attr = db.query(AttributeDefinition).filter_by(code="color").first()
    material_attr = db.query(AttributeDefinition).filter_by(code="material").first()
    gender_attr = db.query(AttributeDefinition).filter_by(code="gender").first()
    
    # Создаем футболку
    tshirt = Product(
        store_id=official_store.id,
        category_id=mens_clothing.id,
        brand_id=nike_brand.id,
        sku="NIKE-TSHIRT-001",
        name="Nike Dri-FIT Мужская футболка",
        slug="nike-dri-fit-mens-tshirt",
        description="""
        Мужская футболка Nike Dri-FIT изготовлена из мягкой влагоотводящей ткани, 
        которая обеспечивает комфорт во время тренировок. Классический крой и 
        минималистичный дизайн делают эту футболку универсальной для спорта и повседневной носки.
        
        Особенности:
        - Технология Dri-FIT отводит влагу от кожи
        - Мягкая и легкая ткань
        - Классический крой
        - Вышитый логотип Nike
        """,
        short_description="Классическая спортивная футболка с технологией Dri-FIT",
        price=2990.00,
        compare_price=3990.00,
        status=ProductStatus.ACTIVE,
        visibility=ProductVisibility.PUBLISHED,
        track_inventory=True,
        stock_quantity=0,  # Склад будет на вариантах
        low_stock_threshold=5,
        meta_title="Nike Dri-FIT Мужская футболка - Купить в Official Store",
        meta_description="Мужская футболка Nike Dri-FIT с влагоотводящей технологией. Размеры S-XXL. Бесплатная доставка от 5000 руб.",
        tags=["nike", "спорт", "футболка", "dri-fit", "новинка"]
    )
    db.add(tshirt)
    db.flush()
    
    # Добавляем общие атрибуты товара (не вариантные)
    if material_attr:
        cotton_poly = db.query(AttributeValue).filter_by(
            attribute_id=material_attr.id,
            value="cotton_poly"
        ).first()
        if cotton_poly:
            db.add(ProductAttribute(
                product_id=tshirt.id,
                attribute_id=material_attr.id,
                attribute_value_id=cotton_poly.id
            ))
    
    if gender_attr:
        male = db.query(AttributeValue).filter_by(
            attribute_id=gender_attr.id,
            value="male"
        ).first()
        if male:
            db.add(ProductAttribute(
                product_id=tshirt.id,
                attribute_id=gender_attr.id,
                attribute_value_id=male.id
            ))
    
    # Создаем варианты товара
    # Получаем значения размеров и цветов
    sizes = db.query(AttributeValue).filter_by(attribute_id=size_attr.id).order_by(AttributeValue.sort_order).all()
    colors = db.query(AttributeValue).filter_by(attribute_id=color_attr.id).all()
    
    # Выберем несколько цветов для футболки
    selected_colors = ["black", "white", "navy"]
    selected_color_values = [c for c in colors if c.value in selected_colors]
    
    variant_count = 0
    for color_value in selected_color_values:
        for size_value in sizes:
            # Создаем вариант
            variant = ProductVariant(
                product_id=tshirt.id,
                name=f"{color_value.display_name} {size_value.display_name}",
                sku=f"NIKE-TSHIRT-001-{color_value.value.upper()}-{size_value.value.upper()}",
                price=2990.00 if size_value.value != "xxl" else 3190.00,  # XXL дороже
                stock_quantity=random.randint(0, 20),  # Случайный остаток
                attributes={
                    "color": color_value.display_name,
                    "size": size_value.display_name,
                    "color_code": color_value.meta_data.get("hex", "#000000")
                },
                sort_order=variant_count,
                is_active=True
            )
            db.add(variant)
            db.flush()
            
            # Добавляем атрибуты варианта
            # Цвет
            db.add(ProductAttribute(
                product_id=tshirt.id,
                variant_id=variant.id,
                attribute_id=color_attr.id,
                attribute_value_id=color_value.id
            ))
            
            # Размер
            db.add(ProductAttribute(
                product_id=tshirt.id,
                variant_id=variant.id,
                attribute_id=size_attr.id,
                attribute_value_id=size_value.id
            ))
            
            variant_count += 1
    
    db.commit()
    logger.info(f"✅ Created product with {variant_count} variants")
    return [tshirt]

# Обновляем функцию seed_database
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
        stores = create_test_stores(db, users)
        attributes = create_test_attributes(db)
        assign_attributes_to_categories(db, categories, attributes)
        products = create_test_products(db, stores, categories, brands)
        
        logger.info("✅ Database seeded successfully!")
        logger.info(f"Created: {len(users)} users, {len(stores)} stores, {len(products)} products")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

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