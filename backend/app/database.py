# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Используем рабочий URL
DATABASE_URL = "postgresql://postgres:Petya9644@127.0.0.1:5432/marketplace"

# Создаем engine для SQLAlchemy 2.x
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Установите True для отладки SQL запросов
    pool_pre_ping=True
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base = declarative_base()

# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()