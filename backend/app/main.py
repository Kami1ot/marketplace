# app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.database import engine, Base, get_db
from app.config import settings

# Импортируем ВСЕ модели (важно для создания таблиц!)
from app.models import *

# Импортируем роутеры
from app.api.v1 import auth, users, products, stores, categories, cart, attributes

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание приложения
app = FastAPI(
    title="Marketplace API",
    description="API для маркетплейса с расширенной функциональностью",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Событие при запуске приложения
@app.on_event("startup")
async def startup_event():
    """Создание таблиц при запуске приложения"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise

# Подключение роутеров API v1
app.include_router(auth.router, prefix="/api/v1/auth", tags=["🔐 Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["👤 Users"])
app.include_router(products.router, prefix="/api/v1/products", tags=["📦 Products"])
app.include_router(stores.router, prefix="/api/v1/stores", tags=["🏪 Stores"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["📁 Categories"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["🛒 Cart"])
app.include_router(attributes.router, prefix="/api/v1/attributes", tags=["📋 Attributes"])

# Главная страница
@app.get("/", tags=["🏠 General"])
async def root():
    """Главная страница API"""
    return {
        "message": "🚀 Marketplace API v2.0",
        "version": "2.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "products": "/api/v1/products",
            "stores": "/api/v1/stores",
            "categories": "/api/v1/categories",
            "cart": "/api/v1/cart"
        }
    }

# Проверка здоровья системы
@app.get("/health", tags=["🏠 General"])
async def health_check(db: Session = Depends(get_db)):
    """Проверка здоровья системы"""
    try:
        # Проверяем подключение к БД
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return {
        "status": "✅ healthy", 
        "version": "2.0.0",
        "database": db_status,
        "endpoints": {
            "total": 6,
            "active": ["auth", "users", "products", "stores", "categories", "cart"]
        }
    }

# Статистика API
@app.get("/api/stats", tags=["🏠 General"])
async def api_statistics(db: Session = Depends(get_db)):
    """Получить статистику использования API"""
    try:
        stats = {
            "users": {
                "total": db.query(User).count(),
                "active": db.query(User).filter(User.status == "active").count(),
                "sellers": db.query(User).filter(User.role == "seller").count()
            },
            "products": {
                "total": db.query(Product).count(),
                "active": db.query(Product).filter(Product.status == "active").count(),
                "categories": db.query(Category).filter(Category.is_active == True).count()
            },
            "stores": {
                "total": db.query(Store).count(),
                "active": db.query(Store).filter(Store.status == "active").count(),
                "verified": db.query(Store).filter(Store.verification_status == "verified").count()
            },
            "orders": {
                "total": db.query(Order).count() if 'Order' in globals() else 0
            }
        }
        return {"status": "success", "data": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Marketplace API...")
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )