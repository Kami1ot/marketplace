# app/schemas/notification.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# === ENUMS ===

class NotificationType(str, Enum):
    ORDER_UPDATE = "order_update"
    PAYMENT_UPDATE = "payment_update"
    REVIEW_RECEIVED = "review_received"
    MESSAGE_RECEIVED = "message_received"
    PROMOTION = "promotion"
    SYSTEM = "system"
    WISHLIST_SALE = "wishlist_sale"
    STOCK_ALERT = "stock_alert"
    PRICE_DROP = "price_drop"
    STORE_UPDATE = "store_update"
    PRODUCT_UPDATE = "product_update"

class NotificationUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    DISMISSED = "dismissed"

class NotificationFilter(str, Enum):
    ALL = "all"
    UNREAD = "unread"
    READ = "read"
    RECENT = "recent"
    HIGH_PRIORITY = "high_priority"
    ORDER_RELATED = "order_related"
    PROMOTIONAL = "promotional"

class NotificationDeliveryMethod(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

# === NOTIFICATION SCHEMAS ===

class NotificationBase(BaseModel):
    user_id: int
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    """Схема для создания уведомления"""
    pass

class NotificationUpdate(BaseModel):
    """Схема для обновления уведомления"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    is_read: Optional[bool] = None

class NotificationResponse(NotificationBase):
    """Схема для ответа с уведомлением"""
    id: int
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    is_unread: bool
    hours_since_created: int
    is_recent: bool
    is_old: bool
    urgency_level: NotificationUrgency
    icon: str
    can_be_dismissed: bool
    requires_action: bool
    action_url: Optional[str] = None
    related_object_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class NotificationSimple(BaseModel):
    """Упрощенная схема уведомления"""
    id: int
    type: NotificationType
    title: str
    is_read: bool
    created_at: datetime
    urgency_level: NotificationUrgency
    icon: str
    
    class Config:
        from_attributes = True

class NotificationWithUser(NotificationResponse):
    """Уведомление с информацией о пользователе"""
    user: Optional['UserSimple'] = None
    
    class Config:
        from_attributes = True

class NotificationSummary(BaseModel):
    """Сводка уведомлений пользователя"""
    total_count: int
    unread_count: int
    high_priority_count: int
    recent_count: int
    by_type: Dict[str, int]  # Количество по типам
    
    class Config:
        from_attributes = True

class NotificationList(BaseModel):
    """Схема для списка уведомлений с пагинацией"""
    notifications: List[NotificationResponse]
    total: int
    page: int
    size: int
    pages: int
    unread_count: int
    summary: Optional[NotificationSummary] = None

class NotificationFilterSchema(BaseModel):
    """Схема для фильтрации уведомлений"""
    user_id: Optional[int] = None
    type: Optional[NotificationType] = None
    filter_type: Optional[NotificationFilter] = None
    is_read: Optional[bool] = None
    urgency: Optional[NotificationUrgency] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None  # Поиск по заголовку и содержанию
    related_object_id: Optional[int] = None

# === NOTIFICATION OPERATIONS SCHEMAS ===

class NotificationMarkAsRead(BaseModel):
    """Схема для отметки уведомления как прочитанного"""
    notification_ids: Optional[List[int]] = None  # Если None, то все уведомления пользователя

class NotificationBulkAction(BaseModel):
    """Схема для массовых действий с уведомлениями"""
    notification_ids: List[int]
    action: str  # "mark_read", "mark_unread", "delete", "archive"

class NotificationDismiss(BaseModel):
    """Схема для отклонения уведомления"""
    notification_ids: List[int]
    reason: Optional[str] = None

class NotificationSettings(BaseModel):
    """Настройки уведомлений пользователя"""
    user_id: int
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    order_updates: bool = True
    promotional: bool = True
    price_alerts: bool = True
    stock_alerts: bool = True
    messages: bool = True
    reviews: bool = True
    quiet_hours_start: Optional[int] = Field(None, ge=0, le=23)  # Час начала тихого времени
    quiet_hours_end: Optional[int] = Field(None, ge=0, le=23)    # Час окончания тихого времени
    
    class Config:
        from_attributes = True

class NotificationPreferences(BaseModel):
    """Предпочтения доставки уведомлений"""
    type: NotificationType
    methods: List[NotificationDeliveryMethod]
    enabled: bool = True
    delay_minutes: int = Field(default=0, ge=0, le=1440)  # Задержка в минутах
    
    class Config:
        from_attributes = True

# === NOTIFICATION DELIVERY SCHEMAS ===

class NotificationDelivery(BaseModel):
    """Доставка уведомления"""
    notification_id: int
    method: NotificationDeliveryMethod
    status: str  # "pending", "sent", "delivered", "failed"
    attempts: int = 0
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class NotificationQueue(BaseModel):
    """Очередь уведомлений"""
    user_id: int
    notifications: List[NotificationCreate]
    delivery_method: NotificationDeliveryMethod
    schedule_at: Optional[datetime] = None
    priority: int = Field(default=5, ge=1, le=10)  # Приоритет доставки

class NotificationBatch(BaseModel):
    """Пакетная отправка уведомлений"""
    user_ids: List[int]
    notification: NotificationCreate
    delivery_methods: List[NotificationDeliveryMethod]
    schedule_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# === NOTIFICATION TEMPLATES SCHEMAS ===

class NotificationTemplate(BaseModel):
    """Шаблон уведомления"""
    id: int
    type: NotificationType
    name: str
    title_template: str
    content_template: str
    variables: List[str]  # Список доступных переменных
    is_active: bool = True
    
    class Config:
        from_attributes = True

class NotificationTemplateCreate(BaseModel):
    """Создание шаблона уведомления"""
    type: NotificationType
    name: str = Field(..., min_length=1, max_length=100)
    title_template: str = Field(..., min_length=1, max_length=255)
    content_template: str
    variables: List[str] = []
    is_active: bool = True

class NotificationFromTemplate(BaseModel):
    """Создание уведомления из шаблона"""
    template_id: int
    user_id: int
    variables: Dict[str, Any]  # Значения для подстановки в шаблон
    delivery_methods: Optional[List[NotificationDeliveryMethod]] = None

# === NOTIFICATION ANALYTICS SCHEMAS ===

class NotificationAnalytics(BaseModel):
    """Аналитика уведомлений"""
    total_sent: int
    total_read: int
    read_rate: float
    avg_read_time: float  # Среднее время до прочтения в часах
    by_type: Dict[str, Dict[str, Any]]  # Статистика по типам
    by_urgency: Dict[str, int]
    delivery_stats: Dict[str, Dict[str, Any]]  # Статистика доставки
    
    class Config:
        from_attributes = True

class NotificationTypeMetrics(BaseModel):
    """Метрики по типу уведомлений"""
    type: NotificationType
    sent_count: int
    read_count: int
    read_rate: float
    avg_read_time: float
    click_rate: float  # Процент кликов по уведомлениям
    
    class Config:
        from_attributes = True

class NotificationTrends(BaseModel):
    """Тренды уведомлений"""
    period: str
    notifications_sent: int
    notifications_read: int
    engagement_rate: float
    trend_change: float  # Изменение в процентах
    peak_hours: List[int]  # Часы пиковой активности
    
    class Config:
        from_attributes = True

class UserNotificationBehavior(BaseModel):
    """Поведение пользователя с уведомлениями"""
    user_id: int
    total_received: int
    total_read: int
    read_rate: float
    avg_read_delay: float  # Среднее время задержки чтения
    preferred_read_times: List[int]  # Предпочитаемые часы чтения
    most_engaged_types: List[NotificationType]
    
    class Config:
        from_attributes = True

# === NOTIFICATION CAMPAIGNS SCHEMAS ===

class NotificationCampaign(BaseModel):
    """Кампания уведомлений"""
    id: int
    name: str
    description: Optional[str] = None
    template_id: int
    target_criteria: Dict[str, Any]  # Критерии выбора пользователей
    schedule_at: Optional[datetime] = None
    status: str  # "draft", "scheduled", "running", "completed", "cancelled"
    
    class Config:
        from_attributes = True

class NotificationCampaignCreate(BaseModel):
    """Создание кампании уведомлений"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    template_id: int
    target_criteria: Dict[str, Any]
    delivery_methods: List[NotificationDeliveryMethod]
    schedule_at: Optional[datetime] = None

class NotificationCampaignStats(BaseModel):
    """Статистика кампании"""
    campaign_id: int
    target_users: int
    sent_count: int
    delivered_count: int
    read_count: int
    click_count: int
    conversion_count: int  # Если отслеживаются конверсии
    
    class Config:
        from_attributes = True

# === REAL-TIME NOTIFICATION SCHEMAS ===

class NotificationWebSocket(BaseModel):
    """WebSocket уведомление"""
    type: str = "notification"
    notification: NotificationResponse
    user_id: int

class NotificationPush(BaseModel):
    """Push уведомление"""
    title: str
    body: str
    icon: Optional[str] = None
    badge: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None

class NotificationEmail(BaseModel):
    """Email уведомление"""
    to: str
    subject: str
    template: str
    variables: Dict[str, Any]
    attachments: Optional[List[str]] = None

class NotificationSMS(BaseModel):
    """SMS уведомление"""
    phone: str
    message: str
    template_id: Optional[str] = None

# === NOTIFICATION WEBHOOKS SCHEMAS ===

class NotificationWebhook(BaseModel):
    """Webhook уведомление"""
    url: str
    method: str = "POST"
    headers: Optional[Dict[str, str]] = None
    payload: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3

class NotificationWebhookResult(BaseModel):
    """Результат webhook уведомления"""
    webhook_id: int
    status_code: int
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    delivered_at: datetime
    
    class Config:
        from_attributes = True

# Для обратной совместимости с импортами моделей
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserSimple