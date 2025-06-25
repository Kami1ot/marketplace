# app/models/discount.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, DECIMAL, Enum, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class DiscountType(str, enum.Enum):
    PERCENTAGE = "percentage"       # Процентная скидка
    FIXED_AMOUNT = "fixed_amount"   # Фиксированная сумма
    FREE_SHIPPING = "free_shipping" # Бесплатная доставка

class DiscountCode(Base):
    __tablename__ = "discount_codes"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Тип и значение скидки
    type = Column(Enum(DiscountType), nullable=False)
    value = Column(DECIMAL(15, 2), nullable=False)  # Процент или сумма
    
    # Условия применения
    minimum_amount = Column(DECIMAL(15, 2), nullable=True)  # Минимальная сумма заказа
    
    # Ограничения использования
    usage_limit = Column(Integer, nullable=True)     # Максимальное количество использований
    usage_count = Column(Integer, default=0, nullable=False)  # Текущее количество использований
    
    # Временные ограничения
    starts_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Статус
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    usages = relationship("DiscountUsage", back_populates="discount_code", cascade="all, delete-orphan")
    
    # Ограничения
    __table_args__ = (
        CheckConstraint('value > 0', name='discount_positive_value'),
        CheckConstraint('usage_limit IS NULL OR usage_limit > 0', name='discount_positive_usage_limit'),
    )
    
    def __repr__(self):
        return f"<DiscountCode(id={self.id}, code='{self.code}', type='{self.type}', value={self.value})>"
    
    @property
    def is_valid(self):
        """Действителен ли промокод"""
        from datetime import datetime
        now = datetime.now()
        
        # Проверяем активность
        if not self.is_active:
            return False
        
        # Проверяем даты
        if self.starts_at and now < self.starts_at:
            return False
        
        if self.expires_at and now > self.expires_at:
            return False
        
        # Проверяем лимит использований
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        
        return True
    
    @property
    def is_expired(self):
        """Истек ли промокод"""
        if not self.expires_at:
            return False
        from datetime import datetime
        return datetime.now() > self.expires_at
    
    @property
    def is_exhausted(self):
        """Исчерпан ли лимит использований"""
        if not self.usage_limit:
            return False
        return self.usage_count >= self.usage_limit
    
    @property
    def is_not_started(self):
        """Еще не начал действовать"""
        if not self.starts_at:
            return False
        from datetime import datetime
        return datetime.now() < self.starts_at
    
    @property
    def remaining_uses(self):
        """Оставшееся количество использований"""
        if not self.usage_limit:
            return None
        return max(0, self.usage_limit - self.usage_count)
    
    @property
    def usage_percentage(self):
        """Процент использования лимита"""
        if not self.usage_limit:
            return 0
        return round((self.usage_count / self.usage_limit) * 100, 1)
    
    @property
    def time_remaining(self):
        """Время до истечения промокода"""
        if not self.expires_at:
            return None
        
        from datetime import datetime
        now = datetime.now()
        if now >= self.expires_at:
            return None
        
        delta = self.expires_at - now
        return {
            "days": delta.days,
            "hours": delta.seconds // 3600,
            "minutes": (delta.seconds % 3600) // 60
        }
    
    def can_be_used_by_user(self, user_id):
        """Может ли пользователь использовать промокод"""
        if not self.is_valid:
            return False
        
        # Здесь можно добавить дополнительные проверки,
        # например, ограничение на одно использование на пользователя
        user_usage_count = len([u for u in self.usages if u.user_id == user_id])
        
        # Пример: один раз на пользователя
        # return user_usage_count == 0
        
        return True
    
    def can_be_applied_to_amount(self, amount):
        """Может ли промокод быть применен к сумме"""
        if not self.is_valid:
            return False
        
        if self.minimum_amount and amount < self.minimum_amount:
            return False
        
        return True
    
    def calculate_discount(self, amount):
        """Рассчитать размер скидки для суммы"""
        if not self.can_be_applied_to_amount(amount):
            return 0
        
        if self.type == DiscountType.PERCENTAGE:
            return min(amount * (self.value / 100), amount)
        elif self.type == DiscountType.FIXED_AMOUNT:
            return min(self.value, amount)
        elif self.type == DiscountType.FREE_SHIPPING:
            return 0  # Обрабатывается отдельно
        
        return 0
    
    @property
    def display_value(self):
        """Отображаемое значение скидки"""
        if self.type == DiscountType.PERCENTAGE:
            return f"{self.value}%"
        elif self.type == DiscountType.FIXED_AMOUNT:
            return f"{self.value} ₽"
        elif self.type == DiscountType.FREE_SHIPPING:
            return "Бесплатная доставка"
        return str(self.value)
    
    @property
    def display_conditions(self):
        """Отображаемые условия применения"""
        conditions = []
        
        if self.minimum_amount:
            conditions.append(f"От {self.minimum_amount} ₽")
        
        if self.usage_limit:
            conditions.append(f"Лимит: {self.usage_limit} использований")
        
        if self.expires_at:
            conditions.append(f"До {self.expires_at.strftime('%d.%m.%Y')}")
        
        return " • ".join(conditions) if conditions else "Без ограничений"
    
    def use_code(self, order_id, user_id, amount):
        """Использовать промокод"""
        if not self.can_be_applied_to_amount(amount):
            raise ValueError("Промокод не может быть применен к данной сумме")
        
        discount_amount = self.calculate_discount(amount)
        
        # Создаем запись об использовании
        usage = DiscountUsage(
            discount_code_id=self.id,
            order_id=order_id,
            user_id=user_id,
            amount=discount_amount
        )
        
        # Увеличиваем счетчик использований
        self.usage_count += 1
        
        return usage


class DiscountUsage(Base):
    __tablename__ = "discount_usages"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    discount_code_id = Column(Integer, ForeignKey("discount_codes.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Размер примененной скидки
    amount = Column(DECIMAL(15, 2), nullable=False)
    
    # Временная метка
    used_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Отношения
    discount_code = relationship("DiscountCode", back_populates="usages")
    order = relationship("Order", back_populates="discount_usages")
    user = relationship("User", back_populates="discount_usages")
    
    def __repr__(self):
        return f"<DiscountUsage(id={self.id}, code_id={self.discount_code_id}, amount={self.amount})>"
    
    @property
    def code(self):
        """Код промокода"""
        return self.discount_code.code if self.discount_code else None
    
    @property
    def discount_type(self):
        """Тип скидки"""
        return self.discount_code.type if self.discount_code else None
    
    @property
    def days_since_usage(self):
        """Дней с момента использования"""
        from datetime import datetime
        return (datetime.now(self.used_at.tzinfo) - self.used_at).days
    
    @property
    def is_recent_usage(self):
        """Недавнее ли использование (менее 7 дней)"""
        return self.days_since_usage < 7