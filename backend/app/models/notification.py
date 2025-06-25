# app/models/notification.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class NotificationType(str, enum.Enum):
    ORDER_UPDATE = "order_update"           # Обновление заказа
    PAYMENT_UPDATE = "payment_update"       # Обновление платежа
    REVIEW_RECEIVED = "review_received"     # Получен отзыв
    MESSAGE_RECEIVED = "message_received"   # Получено сообщение
    PROMOTION = "promotion"                 # Акция/скидка
    SYSTEM = "system"                      # Системное уведомление
    WISHLIST_SALE = "wishlist_sale"        # Скидка на товар из избранного
    STOCK_ALERT = "stock_alert"            # Товар появился в наличии
    PRICE_DROP = "price_drop"              # Снижение цены
    STORE_UPDATE = "store_update"          # Обновление магазина
    PRODUCT_UPDATE = "product_update"       # Обновление товара

class Notification(Base):
    __tablename__ = "notifications"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Содержание уведомления
    type = Column(Enum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)  # Дополнительные данные (ID заказа, товара и т.д.)
    
    # Статус прочтения
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Временная метка
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Отношения
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type}', read={self.is_read})>"
    
    @property
    def is_unread(self):
        """Не прочитано ли уведомление"""
        return not self.is_read
    
    @property
    def hours_since_created(self):
        """Часов с момента создания"""
        from datetime import datetime
        return int((datetime.now(self.created_at.tzinfo) - self.created_at).total_seconds() / 3600)
    
    @property
    def is_recent(self):
        """Недавнее ли уведомление (менее 24 часов)"""
        return self.hours_since_created < 24
    
    @property
    def is_old(self):
        """Старое ли уведомление (более недели)"""
        return self.hours_since_created > (24 * 7)
    
    @property
    def urgency_level(self):
        """Уровень срочности уведомления"""
        urgent_types = [
            NotificationType.ORDER_UPDATE,
            NotificationType.PAYMENT_UPDATE,
            NotificationType.MESSAGE_RECEIVED
        ]
        
        if self.type in urgent_types:
            return "high"
        elif self.type in [NotificationType.PROMOTION, NotificationType.WISHLIST_SALE]:
            return "medium"
        else:
            return "low"
    
    @property
    def icon(self):
        """Иконка для уведомления"""
        icons = {
            NotificationType.ORDER_UPDATE: "📦",
            NotificationType.PAYMENT_UPDATE: "💳",
            NotificationType.REVIEW_RECEIVED: "⭐",
            NotificationType.MESSAGE_RECEIVED: "💬",
            NotificationType.PROMOTION: "🎉",
            NotificationType.SYSTEM: "⚙️",
            NotificationType.WISHLIST_SALE: "❤️",
            NotificationType.STOCK_ALERT: "📈",
            NotificationType.PRICE_DROP: "💰",
            NotificationType.STORE_UPDATE: "🏪",
            NotificationType.PRODUCT_UPDATE: "📦"
        }
        return icons.get(self.type, "🔔")
    
    def mark_as_read(self):
        """Отметить как прочитанное"""
        self.is_read = True
        self.read_at = func.now()
    
    def get_action_url(self):
        """Получить URL для действия по уведомлению"""
        if not self.data:
            return None
            
        if self.type == NotificationType.ORDER_UPDATE and 'order_id' in self.data:
            return f"/orders/{self.data['order_id']}"
        elif self.type == NotificationType.MESSAGE_RECEIVED and 'conversation_id' in self.data:
            return f"/conversations/{self.data['conversation_id']}"
        elif self.type in [NotificationType.WISHLIST_SALE, NotificationType.STOCK_ALERT, NotificationType.PRICE_DROP] and 'product_id' in self.data:
            return f"/products/{self.data['product_id']}"
        elif self.type == NotificationType.STORE_UPDATE and 'store_id' in self.data:
            return f"/stores/{self.data['store_id']}"
        elif self.type == NotificationType.REVIEW_RECEIVED and 'review_id' in self.data:
            return f"/reviews/{self.data['review_id']}"
        
        return None
    
    def get_related_object_id(self):
        """Получить ID связанного объекта"""
        if not self.data:
            return None
            
        # Приоритетный порядок поиска ID
        id_keys = ['order_id', 'product_id', 'store_id', 'conversation_id', 'review_id', 'user_id']
        
        for key in id_keys:
            if key in self.data:
                return self.data[key]
        
        return None
    
    @property
    def can_be_dismissed(self):
        """Может ли уведомление быть отклонено"""
        # Системные уведомления обычно не отклоняются
        return self.type != NotificationType.SYSTEM
    
    @property
    def requires_action(self):
        """Требует ли уведомление действий от пользователя"""
        action_required_types = [
            NotificationType.ORDER_UPDATE,
            NotificationType.PAYMENT_UPDATE,
            NotificationType.MESSAGE_RECEIVED
        ]
        return self.type in action_required_types