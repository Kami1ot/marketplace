# app/models/review.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Enum, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ReviewStatus(str, enum.Enum):
    PENDING = "pending"      # На модерации
    APPROVED = "approved"    # Одобрен
    REJECTED = "rejected"    # Отклонен

class Review(Base):
    __tablename__ = "reviews"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Содержание отзыва
    rating = Column(Integer, nullable=False, index=True)  # 1-5 звезд
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    images = Column(JSON, nullable=True)  # Массив URL изображений
    
    # Статусы и метки
    is_verified = Column(Boolean, default=False, nullable=False)    # Подтвержденная покупка
    is_featured = Column(Boolean, default=False, nullable=False)    # Рекомендуемый отзыв
    helpful_count = Column(Integer, default=0, nullable=False)      # Количество полезных голосов
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False, index=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    product = relationship("Product", back_populates="reviews")
    order_item = relationship("OrderItem", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    votes = relationship("ReviewVote", back_populates="review", cascade="all, delete-orphan")
    
    # Ограничения
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='review_rating_range'),
        # Один отзыв на товар от пользователя (если не привязан к заказу)
        # UniqueConstraint('product_id', 'user_id', name='unique_product_review'),
    )
    
    def __repr__(self):
        return f"<Review(id={self.id}, product_id={self.product_id}, rating={self.rating}, status='{self.status}')>"
    
    @property
    def is_approved(self):
        """Одобрен ли отзыв"""
        return self.status == ReviewStatus.APPROVED
    
    @property
    def is_from_verified_purchase(self):
        """Из подтвержденной покупки"""
        return self.order_item_id is not None
    
    @property
    def helpful_percentage(self):
        """Процент полезности (полезные голоса / общее количество голосов)"""
        total_votes = len(self.votes)
        if total_votes == 0:
            return 0
        helpful_votes = len([v for v in self.votes if v.is_helpful])
        return round((helpful_votes / total_votes) * 100, 1)
    
    @property
    def reviewer_name(self):
        """Имя автора отзыва"""
        if self.user:
            return self.user.first_name or self.user.email.split('@')[0]
        return "Аноним"
    
    @property
    def days_since_review(self):
        """Дней с момента написания отзыва"""
        from datetime import datetime
        return (datetime.now(self.created_at.tzinfo) - self.created_at).days
    
    @property
    def has_images(self):
        """Есть ли изображения в отзыве"""
        return self.images and len(self.images) > 0


class ReviewVote(Base):
    __tablename__ = "review_votes"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_helpful = Column(Boolean, nullable=False)  # True - полезно, False - не полезно
    
    # Временная метка
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Отношения
    review = relationship("Review", back_populates="votes")
    user = relationship("User", back_populates="review_votes")
    
    # Уникальное ограничение - один голос от пользователя за отзыв
    __table_args__ = (
        UniqueConstraint('review_id', 'user_id', name='unique_review_vote'),
    )
    
    def __repr__(self):
        return f"<ReviewVote(id={self.id}, review_id={self.review_id}, helpful={self.is_helpful})>"