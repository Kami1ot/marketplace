# app/config.py
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

class Settings:
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:Petya9644@127.0.0.1:5432/marketplace")
    secret_key: str = os.getenv("SECRET_KEY", "Petya9644")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings()