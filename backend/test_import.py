# test_sqlalchemy_fixed.py
from sqlalchemy import create_engine, text
import urllib.parse

print("🔧 Тестируем SQLAlchemy подключение (версия 2.x)...")

# Варианты URL для тестирования
urls = [
    "postgresql://postgres:Petya9644@127.0.0.1:5432/marketplace",
    "postgresql://postgres:Petya9644@localhost:5432/marketplace",
    f"postgresql://postgres:{urllib.parse.quote_plus('Petya9644')}@127.0.0.1:5432/marketplace",
    "postgresql+psycopg2://postgres:Petya9644@127.0.0.1:5432/marketplace"
]

for i, url in enumerate(urls, 1):
    print(f"\n📋 Тест {i}: {url}")
    
    try:
        # Создаем engine с минимальными настройками
        engine = create_engine(url, echo=False)
        
        # Тестируем подключение (SQLAlchemy 2.x способ)
        with engine.connect() as connection:
            # В SQLAlchemy 2.x нужно использовать text() для raw SQL
            result = connection.execute(text("SELECT version();")).fetchone()
            print(f"✅ Тест {i} успешен!")
            print(f"📊 PostgreSQL: {result[0][:50]}...")
            
            # Дополнительный тест
            db_result = connection.execute(text("SELECT current_database();")).fetchone()
            print(f"🗄️ База данных: {db_result[0]}")
        
        engine.dispose()
        
        # Если первый тест прошел успешно, используем этот URL
        print(f"\n🎯 Рабочий URL найден: {url}")
        break
        
    except Exception as e:
        print(f"❌ Тест {i} неудачен: {e}")
        print(f"❌ Тип ошибки: {type(e)}")

print("\n💡 SQLAlchemy 2.x требует использования text() для raw SQL запросов.")