# app/models/conversation.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ConversationStatus(str, enum.Enum):
    OPEN = "open"            # Открыт
    CLOSED = "closed"        # Закрыт
    RESOLVED = "resolved"    # Решен

class ConversationPriority(str, enum.Enum):
    LOW = "low"              # Низкий
    NORMAL = "normal"        # Обычный
    HIGH = "high"            # Высокий
    URGENT = "urgent"        # Срочный

class Conversation(Base):
    __tablename__ = "conversations"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    
    # Информация о диалоге
    subject = Column(String(255), nullable=True)
    status = Column(Enum(ConversationStatus), default=ConversationStatus.OPEN, nullable=False)
    priority = Column(Enum(ConversationPriority), default=ConversationPriority.NORMAL, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Отношения
    order = relationship("Order", back_populates="conversations")
    customer = relationship("User", foreign_keys=[customer_id], back_populates="customer_conversations")
    store = relationship("Store", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, customer_id={self.customer_id}, store_id={self.store_id}, status='{self.status}')>"
    
    @property
    def is_active(self):
        """Активен ли диалог"""
        return self.status == ConversationStatus.OPEN
    
    @property
    def messages_count(self):
        """Количество сообщений в диалоге"""
        return len(self.messages)
    
    @property
    def last_message(self):
        """Последнее сообщение"""
        if self.messages:
            return sorted(self.messages, key=lambda m: m.created_at)[-1]
        return None
    
    @property
    def unread_messages_count(self):
        """Количество непрочитанных сообщений"""
        return len([m for m in self.messages if not m.read_at])
    
    @property
    def participants(self):
        """Участники диалога"""
        participants = [self.customer]
        if self.store and self.store.owner:
            participants.append(self.store.owner)
        return participants
    
    @property
    def display_subject(self):
        """Отображаемая тема диалога"""
        if self.subject:
            return self.subject
        elif self.order:
            return f"Заказ #{self.order.order_number}"
        else:
            return f"Диалог с {self.store.name}"
    
    def get_unread_messages_for_user(self, user_id):
        """Непрочитанные сообщения для конкретного пользователя"""
        return [m for m in self.messages if not m.read_at and m.sender_id != user_id]
    
    def mark_messages_as_read(self, user_id):
        """Отметить сообщения как прочитанные для пользователя"""
        for message in self.messages:
            if message.sender_id != user_id and not message.read_at:
                message.read_at = func.now()
    
    def close_conversation(self):
        """Закрыть диалог"""
        self.status = ConversationStatus.CLOSED
        self.closed_at = func.now()


class Message(Base):
    __tablename__ = "messages"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Содержание сообщения
    content = Column(Text, nullable=False)
    attachments = Column(JSON, nullable=True)  # Массив URL файлов
    
    # Настройки
    is_internal = Column(Boolean, default=False, nullable=False)  # Внутреннее сообщение
    
    # Статус прочтения
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Временная метка
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Отношения
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, sender_id={self.sender_id})>"
    
    @property
    def is_read(self):
        """Прочитано ли сообщение"""
        return self.read_at is not None
    
    @property
    def has_attachments(self):
        """Есть ли вложения"""
        return self.attachments and len(self.attachments) > 0
    
    @property
    def sender_name(self):
        """Имя отправителя"""
        return self.sender.full_name if self.sender else "Система"
    
    @property
    def hours_since_sent(self):
        """Часов с момента отправки"""
        from datetime import datetime
        return int((datetime.now(self.created_at.tzinfo) - self.created_at).total_seconds() / 3600)
    
    @property
    def is_recent(self):
        """Недавнее ли сообщение (менее часа)"""
        return self.hours_since_sent < 1
    
    @property
    def attachments_count(self):
        """Количество вложений"""
        return len(self.attachments) if self.attachments else 0
    
    def mark_as_read(self):
        """Отметить как прочитанное"""
        self.read_at = func.now()
    
    def get_preview(self, max_length=100):
        """Получить превью сообщения"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."