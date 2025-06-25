# app/models/category.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    
    # Информация о категории
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    icon_url = Column(Text, nullable=True)
    
    # Настройки
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # SEO поля
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"
    
    @property
    def is_root_category(self):
        """Проверка, является ли категория корневой"""
        return self.parent_id is None
    
    @property
    def has_children(self):
        """Проверка, есть ли у категории подкатегории"""
        return len(self.children) > 0
    
    @property
    def level(self):
        """Уровень вложенности категории"""
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level
    
    @property
    def products_count(self):
        """Количество активных товаров в категории"""
        return len([p for p in self.products if p.is_published])
    
    @property
    def total_products_count(self):
        """Общее количество товаров включая подкатегории"""
        count = self.products_count
        for child in self.children:
            count += child.total_products_count
        return count
    
    def get_full_path(self):
        """Получить полный путь категории"""
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return " > ".join(path)
    
    def get_all_children(self):
        """Получить все дочерние категории (рекурсивно)"""
        children = []
        for child in self.children:
            children.append(child)
            children.extend(child.get_all_children())
        return children
    
    def get_breadcrumbs(self):
        """Получить хлебные крошки"""
        breadcrumbs = []
        current = self
        while current:
            breadcrumbs.insert(0, {
                'id': current.id,
                'name': current.name,
                'slug': current.slug
            })
            current = current.parent
        return breadcrumbs
    
    def get_root_category(self):
        """Получить корневую категорию"""
        current = self
        while current.parent:
            current = current.parent
        return current
    
    def get_siblings(self):
        """Получить категории того же уровня"""
        if self.parent:
            return [c for c in self.parent.children if c.id != self.id]
        else:
            # Для корневых категорий - другие корневые
            from sqlalchemy.orm import object_session
            session = object_session(self)
            return session.query(Category).filter(
                Category.parent_id.is_(None),
                Category.id != self.id,
                Category.is_active == True
            ).all()
    
    def can_be_deleted(self):
        """Может ли категория быть удалена"""
        return not self.has_children and self.products_count == 0