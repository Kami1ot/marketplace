# app/schemas/discount.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

# === ENUMS ===

class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_SHIPPING = "free_shipping"

class DiscountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    EXHAUSTED = "exhausted"
    NOT_STARTED = "not_started"

class DiscountValidationStatus(str, Enum):
    VALID = "valid"
    INVALID_CODE = "invalid_code"
    EXPIRED = "expired"
    EXHAUSTED = "exhausted"
    NOT_STARTED = "not_started"
    MINIMUM_AMOUNT_NOT_MET = "minimum_amount_not_met"
    ALREADY_USED_BY_USER = "already_used_by_user"
    INACTIVE = "inactive"

class DiscountSort(str, Enum):
    CREATED_DESC = "created_desc"
    CREATED_ASC = "created_asc"
    USAGE_DESC = "usage_desc"
    USAGE_ASC = "usage_asc"
    EXPIRES_ASC = "expires_asc"
    VALUE_DESC = "value_desc"

# === DISCOUNT CODE SCHEMAS ===

class DiscountCodeBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=50, description="Код промокода")
    type: DiscountType
    value: Decimal = Field(..., gt=0, decimal_places=2, description="Значение скидки")
    minimum_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Минимальная сумма заказа")

class DiscountCodeCreate(DiscountCodeBase):
    """Схема для создания промокода"""
    usage_limit: Optional[int] = Field(None, gt=0, description="Лимит использований")
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    @validator('expires_at')
    def validate_expires_at(cls, v, values):
        if v and 'starts_at' in values and values['starts_at'] and v <= values['starts_at']:
            raise ValueError('Дата окончания должна быть позже даты начала')
        return v
    
    @validator('value')
    def validate_discount_value(cls, v, values):
        if 'type' in values and values['type'] == DiscountType.PERCENTAGE and v > 100:
            raise ValueError('Процентная скидка не может быть больше 100%')
        return v

class DiscountCodeUpdate(BaseModel):
    """Схема для обновления промокода"""
    type: Optional[DiscountType] = None
    value: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    minimum_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    usage_limit: Optional[int] = Field(None, gt=0)
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class DiscountCodeResponse(DiscountCodeBase):
    """Схема для ответа с промокодом"""
    id: int
    usage_limit: Optional[int] = None
    usage_count: int
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_valid: bool
    is_expired: bool
    is_exhausted: bool
    is_not_started: bool
    remaining_uses: Optional[int] = None
    usage_percentage: float
    display_value: str
    display_conditions: str
    
    class Config:
        from_attributes = True

class DiscountCodeSimple(BaseModel):
    """Упрощенная схема промокода"""
    id: int
    code: str
    type: DiscountType
    value: Decimal
    display_value: str
    is_valid: bool
    
    class Config:
        from_attributes = True

class DiscountCodeWithStats(DiscountCodeResponse):
    """Промокод с расширенной статистикой"""
    total_discount_amount: Decimal
    unique_users_count: int
    avg_order_amount: Decimal
    conversion_rate: float  # Процент использований от показов
    
    class Config:
        from_attributes = True

class DiscountCodeWithUsages(DiscountCodeResponse):
    """Промокод с историей использований"""
    usages: List['DiscountUsageResponse'] = []
    
    class Config:
        from_attributes = True

class DiscountCodeValidation(BaseModel):
    """Результат валидации промокода"""
    code: str
    status: DiscountValidationStatus
    is_valid: bool
    message: str
    discount_amount: Optional[Decimal] = None
    final_amount: Optional[Decimal] = None
    conditions: Optional[str] = None
    
    class Config:
        from_attributes = True

class DiscountCodeList(BaseModel):
    """Схема для списка промокодов с пагинацией"""
    codes: List[DiscountCodeResponse]
    total: int
    page: int
    size: int
    pages: int
    active_count: int
    expired_count: int

class DiscountCodeFilter(BaseModel):
    """Схема для фильтрации промокодов"""
    type: Optional[DiscountType] = None
    status: Optional[DiscountStatus] = None
    is_active: Optional[bool] = None
    is_expired: Optional[bool] = None
    is_exhausted: Optional[bool] = None
    search: Optional[str] = None  # Поиск по коду
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    usage_min: Optional[int] = Field(None, ge=0)
    usage_max: Optional[int] = Field(None, ge=0)
    value_min: Optional[Decimal] = Field(None, ge=0)
    value_max: Optional[Decimal] = Field(None, ge=0)

# === DISCOUNT USAGE SCHEMAS ===

class DiscountUsageBase(BaseModel):
    discount_code_id: int
    order_id: int
    user_id: int
    amount: Decimal = Field(..., ge=0, decimal_places=2, description="Размер примененной скидки")

class DiscountUsageCreate(BaseModel):
    """Схема для создания записи об использовании"""
    order_id: int
    amount: Decimal = Field(..., ge=0, decimal_places=2)

class DiscountUsageResponse(DiscountUsageBase):
    """Схема для ответа с использованием промокода"""
    id: int
    used_at: datetime
    code: Optional[str] = None
    discount_type: Optional[DiscountType] = None
    days_since_usage: int
    is_recent_usage: bool
    
    class Config:
        from_attributes = True

class DiscountUsageSimple(BaseModel):
    """Упрощенная схема использования"""
    id: int
    order_id: int
    amount: Decimal
    used_at: datetime
    
    class Config:
        from_attributes = True

class DiscountUsageWithCode(DiscountUsageResponse):
    """Использование с информацией о промокоде"""
    discount_code: Optional[DiscountCodeSimple] = None
    
    class Config:
        from_attributes = True

class DiscountUsageWithUser(DiscountUsageResponse):
    """Использование с информацией о пользователе"""
    user: Optional['UserSimple'] = None
    
    class Config:
        from_attributes = True

class DiscountUsageWithOrder(DiscountUsageResponse):
    """Использование с информацией о заказе"""
    order: Optional['OrderSimple'] = None
    
    class Config:
        from_attributes = True

class DiscountUsageList(BaseModel):
    """Схема для списка использований с пагинацией"""
    usages: List[DiscountUsageResponse]
    total: int
    page: int
    size: int
    pages: int

class DiscountUsageFilter(BaseModel):
    """Схема для фильтрации использований промокодов"""
    discount_code_id: Optional[int] = None
    order_id: Optional[int] = None
    user_id: Optional[int] = None
    discount_type: Optional[DiscountType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    amount_min: Optional[Decimal] = Field(None, ge=0)
    amount_max: Optional[Decimal] = Field(None, ge=0)
    is_recent: Optional[bool] = None  # Только недавние использования

# === DISCOUNT OPERATIONS SCHEMAS ===

class DiscountApply(BaseModel):
    """Схема для применения скидки"""
    code: str
    order_amount: Decimal = Field(..., gt=0, decimal_places=2)
    user_id: Optional[int] = None

class DiscountApplyResult(BaseModel):
    """Результат применения скидки"""
    success: bool
    code: str
    discount_amount: Decimal
    final_amount: Decimal
    message: str
    discount_type: Optional[DiscountType] = None
    
    class Config:
        from_attributes = True

class DiscountCalculation(BaseModel):
    """Расчет скидки"""
    original_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    discount_percentage: float
    savings: Decimal
    
    class Config:
        from_attributes = True

class DiscountBulkGenerate(BaseModel):
    """Схема для массовой генерации промокодов"""
    prefix: Optional[str] = Field(None, max_length=10, description="Префикс для кодов")
    count: int = Field(..., gt=0, le=1000, description="Количество кодов")
    type: DiscountType
    value: Decimal = Field(..., gt=0, decimal_places=2)
    minimum_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    usage_limit: Optional[int] = Field(None, gt=0)
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    length: int = Field(default=8, ge=4, le=20, description="Длина кода")
    
    @validator('expires_at')
    def validate_expires_at(cls, v, values):
        if v and 'starts_at' in values and values['starts_at'] and v <= values['starts_at']:
            raise ValueError('Дата окончания должна быть позже даты начала')
        return v

class DiscountBulkResult(BaseModel):
    """Результат массовой генерации"""
    generated_count: int
    codes: List[str]
    failed_count: int
    errors: List[str] = []
    
    class Config:
        from_attributes = True

# === DISCOUNT ANALYTICS SCHEMAS ===

class DiscountAnalytics(BaseModel):
    """Аналитика системы скидок"""
    total_codes: int
    active_codes: int
    total_usages: int
    total_discount_amount: Decimal
    avg_discount_per_order: Decimal
    most_popular_codes: List[Dict[str, Any]]
    conversion_rate: float  # Процент заказов со скидками
    
    class Config:
        from_attributes = True

class DiscountCodeMetrics(BaseModel):
    """Метрики промокода"""
    code: str
    total_usages: int
    unique_users: int
    total_discount_amount: Decimal
    avg_order_amount: Decimal
    conversion_rate: float
    roi: Optional[float] = None  # Return on Investment
    
    class Config:
        from_attributes = True

class DiscountTrends(BaseModel):
    """Тренды использования скидок"""
    period: str
    usages_count: int
    discount_amount: Decimal
    orders_with_discount: int
    avg_discount_percentage: float
    trend_change: float  # Изменение в процентах к предыдущему периоду
    
    class Config:
        from_attributes = True

class DiscountPerformanceReport(BaseModel):
    """Отчет о эффективности скидок"""
    period_start: datetime
    period_end: datetime
    total_codes_created: int
    total_codes_used: int
    total_discount_amount: Decimal
    total_orders_affected: int
    avg_order_value_with_discount: Decimal
    avg_order_value_without_discount: Decimal
    top_performing_codes: List[DiscountCodeMetrics]
    
    class Config:
        from_attributes = True

# === DISCOUNT RECOMMENDATIONS SCHEMAS ===

class DiscountRecommendation(BaseModel):
    """Рекомендация скидки для пользователя"""
    user_id: int
    recommended_codes: List[DiscountCodeSimple]
    reason: str
    potential_savings: Decimal
    
    class Config:
        from_attributes = True

class DiscountPersonalization(BaseModel):
    """Персонализированные скидки"""
    user_id: int
    purchase_history_value: Decimal
    recommended_discount_type: DiscountType
    recommended_value: Decimal
    target_categories: List[str]
    
    class Config:
        from_attributes = True

# === DISCOUNT NOTIFICATIONS SCHEMAS ===

class DiscountNotification(BaseModel):
    """Уведомление о скидке"""
    type: str  # "expiring_soon", "new_discount", "exclusive_offer"
    title: str
    message: str
    discount_codes: List[str]
    target_users: Optional[List[int]] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DiscountEmail(BaseModel):
    """Email рассылка со скидками"""
    subject: str
    template: str
    discount_codes: List[str]
    target_segment: str  # "all_users", "vip_customers", "abandoned_cart"
    send_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Для обратной совместимости с импортами моделей
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserSimple
    from app.schemas.order import OrderSimple