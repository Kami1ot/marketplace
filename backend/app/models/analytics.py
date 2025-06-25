# app/models/analytics.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class ProductView(Base):
    __tablename__ = "product_views"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Информация о сессии
    session_id = Column(String(255), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)  # Поддержка IPv6
    user_agent = Column(Text, nullable=True)
    referrer = Column(Text, nullable=True)
    
    # Временная метка
    viewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Отношения
    product = relationship("Product", back_populates="views")
    user = relationship("User", back_populates="product_views")
    
    def __repr__(self):
        return f"<ProductView(id={self.id}, product_id={self.product_id}, user_id={self.user_id})>"
    
    @property
    def is_authenticated_view(self):
        """Просмотр от зарегистрированного пользователя"""
        return self.user_id is not None
    
    @property
    def hours_since_view(self):
        """Часов с момента просмотра"""
        from datetime import datetime
        return int((datetime.now(self.viewed_at.tzinfo) - self.viewed_at).total_seconds() / 3600)
    
    @property
    def is_recent_view(self):
        """Недавний ли просмотр (менее 24 часов)"""
        return self.hours_since_view < 24
    
    @property
    def viewer_type(self):
        """Тип просматривающего"""
        if self.user_id:
            return "registered"
        elif self.session_id:
            return "guest"
        else:
            return "anonymous"
    
    @property
    def is_mobile_view(self):
        """Просмотр с мобильного устройства"""
        if not self.user_agent:
            return False
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'tablet']
        return any(keyword in self.user_agent.lower() for keyword in mobile_keywords)
    
    @property
    def browser_info(self):
        """Информация о браузере"""
        if not self.user_agent:
            return "unknown"
        
        ua = self.user_agent.lower()
        if 'chrome' in ua:
            return "chrome"
        elif 'firefox' in ua:
            return "firefox"
        elif 'safari' in ua:
            return "safari"
        elif 'edge' in ua:
            return "edge"
        else:
            return "other"


class SearchLog(Base):
    __tablename__ = "search_logs"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    
    # Поисковая информация
    query = Column(String(500), nullable=False, index=True)
    filters = Column(JSON, nullable=True)    # Примененные фильтры
    results_count = Column(Integer, nullable=True)
    
    # Техническая информация
    ip_address = Column(String(45), nullable=True)
    
    # Временная метка
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<SearchLog(id={self.id}, query='{self.query}', results={self.results_count})>"
    
    @property
    def is_authenticated_search(self):
        """Поиск от зарегистрированного пользователя"""
        return self.user_id is not None
    
    @property
    def has_results(self):
        """Были ли найдены результаты"""
        return self.results_count and self.results_count > 0
    
    @property
    def search_terms(self):
        """Список поисковых терминов"""
        return [term.strip() for term in self.query.lower().split() if term.strip()]
    
    @property
    def search_length(self):
        """Длина поискового запроса"""
        return len(self.query.strip())
    
    @property
    def is_short_query(self):
        """Короткий ли запрос (менее 3 символов)"""
        return self.search_length < 3
    
    @property
    def is_long_query(self):
        """Длинный ли запрос (более 50 символов)"""
        return self.search_length > 50
    
    @property
    def has_filters(self):
        """Применялись ли фильтры"""
        return self.filters and len(self.filters) > 0
    
    @property
    def filters_count(self):
        """Количество примененных фильтров"""
        return len(self.filters) if self.filters else 0
    
    @property
    def is_successful_search(self):
        """Успешный ли поиск (есть результаты)"""
        return self.has_results
    
    @property
    def hours_since_search(self):
        """Часов с момента поиска"""
        from datetime import datetime
        return int((datetime.now(self.created_at.tzinfo) - self.created_at).total_seconds() / 3600)
    
    def get_popular_terms(self):
        """Популярные термины из запроса (длиннее 2 символов)"""
        return [term for term in self.search_terms if len(term) > 2]
    
    def is_similar_to(self, other_query):
        """Похож ли запрос на другой"""
        if not other_query:
            return False
        
        terms1 = set(self.search_terms)
        terms2 = set([term.strip() for term in other_query.lower().split() if term.strip()])
        
        if not terms1 or not terms2:
            return False
        
        # Вычисляем пересечение
        intersection = terms1.intersection(terms2)
        union = terms1.union(terms2)
        
        # Коэффициент Жаккара
        similarity = len(intersection) / len(union) if union else 0
        return similarity > 0.5