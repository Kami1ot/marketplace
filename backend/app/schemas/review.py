# app/schemas/review.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# === ENUMS ===

class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ReviewSort(str, Enum):
    NEWEST = "newest"
    OLDEST = "oldest"
    RATING_HIGH = "rating_high"
    RATING_LOW = "rating_low"
    HELPFUL = "helpful"
    VERIFIED = "verified"

class ReviewFilter(str, Enum):
    ALL = "all"
    APPROVED = "approved"
    PENDING = "pending"
    VERIFIED = "verified"
    WITH_IMAGES = "with_images"
    FEATURED = "featured"

class RatingFilter(str, Enum):
    ALL = "all"
    FIVE_STARS = "5"
    FOUR_STARS = "4"
    THREE_STARS = "3"
    TWO_STARS = "2"
    ONE_STAR = "1"

# === REVIEW SCHEMAS ===

class ReviewBase(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5 звезд")
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    images: Optional[List[str]] = None  # Список URL изображений

class ReviewCreate(ReviewBase):
    """Схема для создания отзыва"""
    order_item_id: Optional[int] = None  # Привязка к покупке
    
    @validator('images')
    def validate_images_count(cls, v):
        if v and len(v) > 10:  # Ограничение на количество изображений
            raise ValueError('Максимум 10 изображений в отзыве')
        return v

class ReviewUpdate(BaseModel):
    """Схема для обновления отзыва"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    images: Optional[List[str]] = None

class ReviewModerate(BaseModel):
    """Схема для модерации отзыва"""
    status: ReviewStatus
    rejection_reason: Optional[str] = None
    is_featured: Optional[bool] = None

class ReviewResponse(ReviewBase):
    """Схема для ответа с отзывом"""
    id: int
    user_id: int
    order_item_id: Optional[int] = None
    is_verified: bool
    is_featured: bool
    helpful_count: int
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime
    is_approved: bool
    is_from_verified_purchase: bool
    helpful_percentage: float
    reviewer_name: str
    days_since_review: int
    has_images: bool
    
    class Config:
        from_attributes = True

class ReviewSimple(BaseModel):
    """Упрощенная схема отзыва"""
    id: int
    rating: int
    title: Optional[str] = None
    reviewer_name: str
    created_at: datetime
    is_verified: bool
    helpful_count: int
    
    class Config:
        from_attributes = True

class ReviewWithUser(ReviewResponse):
    """Отзыв с информацией о пользователе"""
    user: Optional['UserSimple'] = None
    
    class Config:
        from_attributes = True

class ReviewWithProduct(ReviewResponse):
    """Отзыв с информацией о товаре"""
    product: Optional['ProductSimple'] = None
    
    class Config:
        from_attributes = True

class ReviewWithVotes(ReviewResponse):
    """Отзыв с голосами"""
    votes: List['ReviewVoteResponse'] = []
    user_vote: Optional['ReviewVoteResponse'] = None  # Голос текущего пользователя
    
    class Config:
        from_attributes = True

class ReviewFull(ReviewResponse):
    """Полная информация об отзыве"""
    user: Optional['UserSimple'] = None
    product: Optional['ProductSimple'] = None
    order_item: Optional['OrderItemSimple'] = None
    votes_count: int
    helpful_votes_count: int
    
    class Config:
        from_attributes = True

class ReviewList(BaseModel):
    """Схема для списка отзывов с пагинацией"""
    reviews: List[ReviewResponse]
    total: int
    page: int
    size: int
    pages: int
    rating_summary: Optional['RatingSummary'] = None

class ReviewFilter(BaseModel):
    """Схема для фильтрации отзывов"""
    product_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[ReviewStatus] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_verified: Optional[bool] = None
    is_featured: Optional[bool] = None
    has_images: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None  # Поиск по заголовку и содержанию

# === REVIEW VOTE SCHEMAS ===

class ReviewVoteBase(BaseModel):
    is_helpful: bool

class ReviewVoteCreate(ReviewVoteBase):
    """Схема для создания голоса за отзыв"""
    review_id: int

class ReviewVoteUpdate(ReviewVoteBase):
    """Схема для обновления голоса"""
    pass

class ReviewVoteResponse(ReviewVoteBase):
    """Схема для ответа с голосом"""
    id: int
    review_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReviewVoteSimple(BaseModel):
    """Упрощенная схема голоса"""
    is_helpful: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# === REVIEW STATISTICS SCHEMAS ===

class RatingSummary(BaseModel):
    """Сводка рейтингов"""
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[str, int]  # {"5": 45, "4": 23, "3": 12, "2": 8, "1": 2}
    verified_reviews_count: int
    reviews_with_images: int
    
    class Config:
        from_attributes = True

class ProductReviewStats(BaseModel):
    """Статистика отзывов товара"""
    product_id: int
    total_reviews: int
    average_rating: float
    verified_reviews: int
    featured_reviews: int
    pending_reviews: int
    reviews_with_images: int
    helpful_reviews: int  # Отзывы с положительными голосами
    rating_breakdown: Dict[str, int]
    recent_rating_trend: float  # Тренд за последний месяц
    
    class Config:
        from_attributes = True

class UserReviewStats(BaseModel):
    """Статистика отзывов пользователя"""
    user_id: int
    total_reviews: int
    verified_reviews: int
    average_rating_given: float
    helpful_votes_received: int
    featured_reviews: int
    reviews_by_rating: Dict[str, int]
    
    class Config:
        from_attributes = True

class ReviewAnalytics(BaseModel):
    """Аналитика отзывов"""
    total_reviews: int
    approved_reviews: int
    pending_reviews: int
    rejected_reviews: int
    verification_rate: float  # Процент подтвержденных покупок
    average_rating: float
    reviews_with_images_rate: float
    helpful_votes_ratio: float
    
    class Config:
        from_attributes = True

class ReviewTrends(BaseModel):
    """Тренды отзывов"""
    period: str
    reviews_count: int
    average_rating: float
    verification_rate: float
    growth_rate: float  # Рост количества отзывов
    sentiment_score: Optional[float] = None  # Если есть анализ тональности
    
    class Config:
        from_attributes = True

# === REVIEW MODERATION SCHEMAS ===

class ReviewModerationQueue(BaseModel):
    """Очередь модерации отзывов"""
    pending_reviews: List[ReviewResponse]
    total_pending: int
    avg_review_length: float
    reviews_with_images: int
    suspected_spam: int  # Подозрительные отзывы
    
    class Config:
        from_attributes = True

class ReviewModerationAction(BaseModel):
    """Действие модерации"""
    review_ids: List[int]
    action: str  # "approve", "reject", "feature", "unfeature"
    reason: Optional[str] = None
    notify_user: bool = False

class ReviewModerationStats(BaseModel):
    """Статистика модерации"""
    total_moderated: int
    approved_count: int
    rejected_count: int
    approval_rate: float
    avg_moderation_time: float  # В часах
    moderator_stats: Dict[str, Dict[str, Any]]  # Статистика по модераторам
    
    class Config:
        from_attributes = True

# === REVIEW REPORTS SCHEMAS ===

class ReviewSpamReport(BaseModel):
    """Жалоба на спам в отзыве"""
    review_id: int
    reason: str
    description: Optional[str] = None

class ReviewReport(BaseModel):
    """Жалоба на отзыв"""
    review_id: int
    reporter_id: int
    reason: str  # "spam", "inappropriate", "fake", "offensive"
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class ReviewReportStats(BaseModel):
    """Статистика жалоб"""
    total_reports: int
    reports_by_reason: Dict[str, int]
    resolved_reports: int
    pending_reports: int
    false_positive_rate: float
    
    class Config:
        from_attributes = True

# === REVIEW RECOMMENDATIONS SCHEMAS ===

class ReviewIncentive(BaseModel):
    """Стимул для написания отзыва"""
    user_id: int
    product_id: int
    order_item_id: int
    incentive_type: str  # "discount", "points", "coupon"
    incentive_value: str
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ReviewReminder(BaseModel):
    """Напоминание о написании отзыва"""
    user_id: int
    order_item_id: int
    product_name: str
    days_since_delivery: int
    reminder_sent: bool = False
    
    class Config:
        from_attributes = True

class ReviewSentiment(BaseModel):
    """Анализ тональности отзыва"""
    review_id: int
    sentiment_score: float  # -1 (негативный) до 1 (позитивный)
    sentiment_label: str  # "positive", "negative", "neutral"
    confidence: float
    keywords: List[str]
    
    class Config:
        from_attributes = True

# === REVIEW EXPORT SCHEMAS ===

class ReviewExport(BaseModel):
    """Экспорт отзывов"""
    product_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[ReviewStatus] = None
    format: str = "csv"  # "csv", "xlsx", "json"
    include_votes: bool = False
    include_images: bool = False

class ReviewImport(BaseModel):
    """Импорт отзывов"""
    file_url: str
    format: str  # "csv", "xlsx", "json"
    mapping: Dict[str, str]  # Маппинг полей файла к полям модели
    validate_users: bool = True
    auto_approve: bool = False

# === REVIEW WIDGETS SCHEMAS ===

class ReviewWidget(BaseModel):
    """Виджет отзывов для товара"""
    product_id: int
    average_rating: float
    total_reviews: int
    rating_distribution: Dict[str, int]
    recent_reviews: List[ReviewSimple]
    verified_reviews_count: int
    
    class Config:
        from_attributes = True

class ReviewBadge(BaseModel):
    """Бейдж отзывов"""
    average_rating: float
    total_reviews: int
    badge_type: str  # "minimal", "detailed", "stars_only"
    show_verified: bool = True
    
    class Config:
        from_attributes = True

# === REVIEW NOTIFICATIONS SCHEMAS ===

class ReviewNotification(BaseModel):
    """Уведомление об отзыве"""
    type: str  # "new_review", "review_approved", "review_rejected", "helpful_vote"
    review_id: int
    recipient_id: int
    message: str
    
    class Config:
        from_attributes = True

class ReviewEmailTemplate(BaseModel):
    """Шаблон email для отзывов"""
    template_type: str  # "review_request", "review_approved", "review_helpful"
    subject: str
    content: str
    variables: List[str]  # Доступные переменные
    
    class Config:
        from_attributes = True

# Для обратной совместимости с импортами моделей
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserSimple
    from app.schemas.product import ProductSimple
    from app.schemas.order import OrderItemSimple