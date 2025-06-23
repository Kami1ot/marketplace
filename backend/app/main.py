# app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

# Импорты для БД
from app.database import engine, Base, get_db
from app.api import auth, products, admin  # Добавлен admin

# Создаем экземпляр FastAPI с улучшенным описанием
app = FastAPI(
    title="Marketplace API",
    description="""
    🛒 **Маркетплейс API с системой ролей**
    
    ## Роли пользователей:
    
    * 👤 **USER** - Может просматривать товары и категории
    * 🏢 **BUSINESS** - Может продавать товары + все права USER
    * 👑 **ADMIN** - Полный доступ ко всему + управление пользователями
    
    ## Особенности:
    
    * 🔐 Безопасная аутентификация с JWT токенами
    * 🛡️ Система разрешений на основе ролей
    * 📊 Статистика и аналитика
    * 🔄 Мягкое удаление (деактивация)
    
    ## Начало работы:
    
    1. Зарегистрируйтесь как обычный пользователь
    2. Обратитесь к админу для получения бизнес-аккаунта
    3. Начните продавать товары!
    """,
    version="2.0.0",
    contact={
        "name": "Marketplace Support",
        "email": "support@marketplace.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты с улучшенными тегами и описаниями
app.include_router(
    auth.router, 
    prefix="/api/auth", 
    tags=["🔐 Authentication"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    products.router, 
    prefix="/api/products", 
    tags=["🛍️ Products"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    admin.router, 
    prefix="/api/admin", 
    tags=["👑 Admin Panel"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
        404: {"description": "Not found"}
    }
)

# Создаем таблицы при запуске приложения
@app.on_event("startup")
async def startup_event():
    # Импортируем ВСЕ модели здесь
    from app.models.user import User, UserRole
    from app.models.category import Category
    from app.models.product import Product
    
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    print("📊 Все таблицы базы данных созданы!")
    
    # Создаем админа если его нет
    from app.core.security import get_password_hash
    from sqlalchemy.orm import sessionmaker
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Проверяем есть ли админ
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            # Создаем первого админа
            admin_user = User(
                email="admin@marketplace.com",
                hashed_password=get_password_hash("admin123"),
                first_name="Super",
                last_name="Admin",
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            print("👑 Создан суперадмин: admin@marketplace.com / admin123")
        else:
            print("👑 Суперадмин уже существует")
    except Exception as e:
        print(f"⚠️ Ошибка создания админа: {e}")
    finally:
        db.close()

@app.get("/", tags=["🏠 General"])
async def root():
    """Главная страница API"""
    return {
        "message": "🛒 Marketplace API v2.0 - Role-Based E-commerce Platform",
        "version": "2.0.0",
        "features": {
            "authentication": "JWT-based secure authentication",
            "roles": {
                "USER": "Browse products and categories",
                "BUSINESS": "Sell products + USER privileges", 
                "ADMIN": "Full platform management"
            },
            "products": "Full CRUD with image support",
            "categories": "Hierarchical organization",
            "soft_delete": "Safe deactivation instead of permanent deletion"
        },
        "endpoints": {
            "docs": "/docs",
            "admin": "/api/admin/*",
            "auth": "/api/auth/*",
            "products": "/api/products/*"
        }
    }

@app.get("/health", tags=["🏠 General"])
async def health_check():
    """Проверка здоровья системы"""
    return {
        "status": "✅ healthy", 
        "version": "2.0.0",
        "database": "connected",
        "auth": "enabled",
        "roles": "active"
    }

@app.get("/test-db", tags=["🏠 General"])
async def test_database(db: Session = Depends(get_db)):
    """Тестирование подключения к базе данных"""
    try:
        from app.models.user import User, UserRole
        from app.models.product import Product
        
        result = db.execute(text("SELECT version();")).fetchone()
        
        user_count = db.query(User).count()
        product_count = db.query(Product).count()
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
        business_count = db.query(User).filter(User.role == UserRole.BUSINESS).count()
        
        return {
            "status": "✅ database connected",
            "postgresql_version": result[0][:50] + "...",
            "statistics": {
                "total_users": user_count,
                "total_products": product_count,
                "admin_users": admin_count,
                "business_users": business_count,
                "regular_users": user_count - admin_count - business_count
            },
            "features": {
                "role_system": "✅ enabled",
                "soft_delete": "✅ enabled",
                "admin_panel": "✅ enabled"
            }
        }
        
    except Exception as e:
        return {
            "status": "❌ database error", 
            "error": str(e)
        }

@app.get("/create-test-data", tags=["🏠 General"])
async def create_test_data(db: Session = Depends(get_db)):
    """Создание тестовых данных для демонстрации"""
    try:
        from app.models.user import User, UserRole
        from app.models.category import Category
        from app.models.product import Product
        from app.core.security import get_password_hash
        
        # Проверяем тестовые данные
        existing_data = db.query(Category).first()
        if existing_data:
            return {
                "message": "ℹ️ Тестовые данные уже существуют",
                "accounts": {
                    "admin": "admin@marketplace.com / admin123",
                    "business": "business@test.com / password", 
                    "user": "user@test.com / password"
                }
            }
        
        # Создаем тестовых пользователей
        users_data = [
            {
                "email": "user@test.com",
                "password": "password",
                "first_name": "John",
                "last_name": "Doe",
                "role": UserRole.USER
            },
            {
                "email": "business@test.com", 
                "password": "password",
                "first_name": "Jane",
                "last_name": "Seller",
                "role": UserRole.BUSINESS
            }
        ]
        
        test_users = []
        for user_data in users_data:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                user = User(
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=user_data["role"]
                )
                db.add(user)
                test_users.append(user)
        
        # Создаем категории
        categories_data = [
            {"name": "🔌 Электроника", "description": "Телефоны, ноутбуки, планшеты"},
            {"name": "👕 Одежда", "description": "Мужская и женская одежда"},
            {"name": "🏠 Дом и сад", "description": "Товары для дома и дачи"},
            {"name": "📚 Книги", "description": "Художественная и техническая литература"},
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.add(category)
            categories.append(category)
        
        db.commit()
        
        # Получаем бизнес-пользователя для создания товаров
        business_user = db.query(User).filter(User.email == "business@test.com").first()
        
        if business_user:
            # Создаем товары
            products_data = [
                {
                    "title": "📱 iPhone 15 Pro",
                    "description": "Новейший смартфон Apple с титановым корпусом",
                    "price": 99999.99,
                    "stock_quantity": 10,
                    "category_id": categories[0].id,
                    "images": ["iphone15.jpg", "iphone15_back.jpg"]
                },
                {
                    "title": "👔 Рубашка классическая",
                    "description": "100% хлопок, размеры S-XL, белый цвет",
                    "price": 2999.99,
                    "stock_quantity": 50,
                    "category_id": categories[1].id,
                    "images": ["shirt_white.jpg"]
                },
                {
                    "title": "🪑 Офисное кресло",
                    "description": "Эргономичное кресло для работы, регулируемая высота",
                    "price": 15999.99,
                    "stock_quantity": 5,
                    "category_id": categories[2].id,
                    "images": ["office_chair.jpg"]
                },
                {
                    "title": "📖 Python для начинающих",
                    "description": "Практическое руководство по программированию на Python",
                    "price": 1499.99,
                    "stock_quantity": 25,
                    "category_id": categories[3].id,
                    "images": ["python_book.jpg"]
                }
            ]
            
            for prod_data in products_data:
                product = Product(**prod_data, seller_id=business_user.id)
                db.add(product)
        
        db.commit()
        
        return {
            "message": "🎉 Тестовые данные созданы успешно!",
            "created": {
                "categories": len(categories_data),
                "products": len(products_data) if business_user else 0,
                "test_users": len(test_users)
            },
            "test_accounts": {
                "👑 admin": "admin@marketplace.com / admin123",
                "🏢 business": "business@test.com / password",
                "👤 user": "user@test.com / password"
            },
            "next_steps": [
                "1. Войдите в /docs для тестирования API",
                "2. Используйте тестовые аккаунты для проверки ролей",
                "3. Админ может управлять пользователями в разделе Admin Panel"
            ]
        }
        
    except Exception as e:
        return {"status": "❌ error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)