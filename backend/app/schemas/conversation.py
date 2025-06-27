# app/schemas/conversation.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# === ENUMS ===

class ConversationStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    RESOLVED = "resolved"

class ConversationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"
    ORDER_UPDATE = "order_update"

class ConversationFilter(str, Enum):
    ALL = "all"
    UNREAD = "unread"
    ACTIVE = "active"
    CLOSED = "closed"
    HIGH_PRIORITY = "high_priority"

# === CONVERSATION SCHEMAS ===

class ConversationBase(BaseModel):
    order_id: Optional[int] = None
    customer_id: int
    store_id: int
    subject: Optional[str] = Field(None, max_length=255)
    priority: ConversationPriority = ConversationPriority.NORMAL

class ConversationCreate(ConversationBase):
    """Схема для создания диалога"""
    initial_message: Optional[str] = Field(None, description="Первое сообщение в диалоге")

class ConversationUpdate(BaseModel):
    """Схема для обновления диалога"""
    subject: Optional[str] = Field(None, max_length=255)
    status: Optional[ConversationStatus] = None
    priority: Optional[ConversationPriority] = None

class ConversationResponse(ConversationBase):
    """Схема для ответа с диалогом"""
    id: int
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    is_active: bool
    messages_count: int
    unread_messages_count: int
    display_subject: str
    
    class Config:
        from_attributes = True

class ConversationSimple(BaseModel):
    """Упрощенная схема диалога для списков"""
    id: int
    subject: Optional[str] = None
    display_subject: str
    status: ConversationStatus
    priority: ConversationPriority
    messages_count: int
    unread_messages_count: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ConversationWithParticipants(ConversationResponse):
    """Диалог с участниками"""
    customer: Optional['UserSimple'] = None
    store: Optional['StoreSimple'] = None
    order: Optional['OrderSimple'] = None
    
    class Config:
        from_attributes = True

class ConversationWithLastMessage(ConversationResponse):
    """Диалог с последним сообщением"""
    last_message: Optional['MessageSimple'] = None
    
    class Config:
        from_attributes = True

class ConversationFull(ConversationWithParticipants):
    """Полная информация о диалоге"""
    messages: List['MessageResponse'] = []
    last_message: Optional['MessageSimple'] = None
    
    class Config:
        from_attributes = True

class ConversationStats(BaseModel):
    """Статистика диалога"""
    id: int
    total_messages: int
    customer_messages: int
    store_messages: int
    avg_response_time: Optional[float] = None  # В часах
    first_response_time: Optional[float] = None  # В часах
    resolution_time: Optional[float] = None  # В часах до закрытия
    
    class Config:
        from_attributes = True

class ConversationList(BaseModel):
    """Схема для списка диалогов с пагинацией"""
    conversations: List[ConversationWithLastMessage]
    total: int
    page: int
    size: int
    pages: int
    unread_total: int

class ConversationFilterSchema(BaseModel):
    """Схема для фильтрации диалогов"""
    customer_id: Optional[int] = None
    store_id: Optional[int] = None
    order_id: Optional[int] = None
    status: Optional[ConversationStatus] = None
    priority: Optional[ConversationPriority] = None
    filter_type: Optional[ConversationFilter] = None
    has_unread: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None  # Поиск по теме или содержанию сообщений

# === MESSAGE SCHEMAS ===

class MessageBase(BaseModel):
    conversation_id: int
    content: str = Field(..., min_length=1)
    attachments: Optional[List[str]] = None  # Список URL файлов
    is_internal: bool = False

class MessageCreate(BaseModel):
    """Схема для создания сообщения"""
    content: str = Field(..., min_length=1)
    attachments: Optional[List[str]] = None
    is_internal: bool = False

class MessageUpdate(BaseModel):
    """Схема для обновления сообщения"""
    content: Optional[str] = Field(None, min_length=1)
    is_internal: Optional[bool] = None

class MessageResponse(MessageBase):
    """Схема для ответа с сообщением"""
    id: int
    sender_id: int
    created_at: datetime
    read_at: Optional[datetime] = None
    is_read: bool
    has_attachments: bool
    sender_name: str
    hours_since_sent: int
    is_recent: bool
    attachments_count: int
    
    class Config:
        from_attributes = True

class MessageSimple(BaseModel):
    """Упрощенная схема сообщения"""
    id: int
    content: str
    sender_id: int
    sender_name: str
    created_at: datetime
    is_read: bool
    has_attachments: bool
    
    class Config:
        from_attributes = True

class MessageWithSender(MessageResponse):
    """Сообщение с информацией об отправителе"""
    sender: Optional['UserSimple'] = None
    
    class Config:
        from_attributes = True

class MessageWithConversation(MessageResponse):
    """Сообщение с информацией о диалоге"""
    conversation: Optional[ConversationSimple] = None
    
    class Config:
        from_attributes = True

class MessagePreview(BaseModel):
    """Превью сообщения"""
    id: int
    preview_text: str
    sender_name: str
    created_at: datetime
    has_attachments: bool
    is_read: bool
    
    class Config:
        from_attributes = True

class MessageList(BaseModel):
    """Схема для списка сообщений с пагинацией"""
    messages: List[MessageResponse]
    total: int
    page: int
    size: int
    pages: int

class MessageFilterSchema(BaseModel):
    """Схема для фильтрации сообщений"""
    conversation_id: Optional[int] = None
    sender_id: Optional[int] = None
    is_read: Optional[bool] = None
    is_internal: Optional[bool] = None
    has_attachments: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None  # Поиск по содержанию

# === CONVERSATION OPERATIONS SCHEMAS ===

class ConversationMarkAsRead(BaseModel):
    """Схема для отметки диалога как прочитанного"""
    user_id: int

class ConversationClose(BaseModel):
    """Схема для закрытия диалога"""
    reason: Optional[str] = None
    final_message: Optional[str] = None

class ConversationReopen(BaseModel):
    """Схема для переоткрытия диалога"""
    reason: Optional[str] = None
    initial_message: Optional[str] = None

class ConversationTransfer(BaseModel):
    """Схема для передачи диалога другому сотруднику"""
    new_assignee_id: int
    reason: Optional[str] = None
    notify_customer: bool = True

class ConversationBulkAction(BaseModel):
    """Схема для массовых действий с диалогами"""
    conversation_ids: List[int]
    action: str  # "close", "mark_read", "change_priority", "archive"
    parameters: Optional[Dict[str, Any]] = None

# === CONVERSATION ANALYTICS SCHEMAS ===

class ConversationAnalytics(BaseModel):
    """Аналитика диалогов"""
    total_conversations: int
    open_conversations: int
    closed_conversations: int
    avg_response_time: float  # В часах
    avg_resolution_time: float  # В часах
    customer_satisfaction: Optional[float] = None  # Если есть система оценок
    busiest_hours: List[int]  # Часы с наибольшим количеством сообщений
    
    class Config:
        from_attributes = True

class StoreConversationMetrics(BaseModel):
    """Метрики диалогов для магазина"""
    store_id: int
    store_name: str
    total_conversations: int
    active_conversations: int
    avg_response_time: float
    unread_messages: int
    customer_satisfaction: Optional[float] = None
    
    class Config:
        from_attributes = True

class ConversationTrends(BaseModel):
    """Тренды диалогов"""
    period: str
    conversations_created: int
    conversations_resolved: int
    avg_messages_per_conversation: float
    response_time_trend: float  # Изменение времени ответа в %
    volume_trend: float  # Изменение объема в %
    
    class Config:
        from_attributes = True

class ResponseTimeMetrics(BaseModel):
    """Метрики времени ответа"""
    avg_first_response: float  # Среднее время первого ответа
    avg_response_time: float   # Среднее время ответа
    median_response_time: float
    response_within_1hour: float  # Процент ответов в течение часа
    response_within_24hours: float  # Процент ответов в течение суток
    
    class Config:
        from_attributes = True

# === CONVERSATION NOTIFICATIONS SCHEMAS ===

class ConversationNotification(BaseModel):
    """Уведомление о диалоге"""
    conversation_id: int
    user_id: int
    type: str  # "new_message", "conversation_closed", "priority_changed"
    title: str
    message: str
    read: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationEmailNotification(BaseModel):
    """Email уведомление о диалоге"""
    conversation_id: int
    recipient_email: str
    template: str
    subject: str
    variables: Dict[str, Any]  # Переменные для шаблона

class ConversationDigest(BaseModel):
    """Дайджест диалогов"""
    user_id: int
    period: str  # "daily", "weekly"
    unread_conversations: int
    new_conversations: int
    urgent_conversations: int
    conversations_summary: List[ConversationSimple]
    
    class Config:
        from_attributes = True

# === CONVERSATION TEMPLATES SCHEMAS ===

class ConversationTemplate(BaseModel):
    """Шаблон сообщения"""
    id: int
    name: str
    content: str
    category: str  # "greeting", "closing", "apology", "instruction"
    is_active: bool
    
    class Config:
        from_attributes = True

class ConversationQuickReply(BaseModel):
    """Быстрый ответ"""
    text: str
    category: Optional[str] = None
    
    class Config:
        from_attributes = True

# Для обратной совместимости с импортами моделей
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserSimple
    from app.schemas.store import StoreSimple
    from app.schemas.order import OrderSimple