# app/schemas/__init__.py

# User schemas
from app.schemas.user import (
    UserBase, UserCreate, UserCreateAdmin, UserUpdate, UserUpdateRole, 
    UserUpdateStatus, UserResponse, UserSimple, UserWithProfile, UserWithAddresses,
    UserProfileBase, UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    UserAddressBase, UserAddressCreate, UserAddressUpdate, UserAddressResponse,
    UserLogin, Token, TokenData, PasswordChange, PasswordReset, PasswordResetConfirm,
    UserRole, UserStatus, AddressType
)

# Product schemas
from app.schemas.product import (
    ProductBase, ProductCreate, ProductUpdate, ProductResponse, ProductSimple,
    ProductWithDetails, ProductWithVariants, ProductList, ProductFilter, ProductSort,
    ProductVariantBase, ProductVariantCreate, ProductVariantUpdate, ProductVariantResponse,
    ProductVariantWithImages, ProductImageBase, ProductImageCreate, ProductImageUpdate,
    ProductImageResponse, ProductStatus, ProductVisibility
)

# Category schemas
from app.schemas.category import (
    CategoryBase, CategoryCreate, CategoryUpdate, CategoryResponse, CategorySimple,
    CategoryWithChildren, CategoryTree, CategoryList,
    CategoryFilter, CategoryStats
)

# Brand schemas
from app.schemas.brand import (
    BrandBase, BrandCreate, BrandUpdate, BrandResponse, BrandSimple,
    BrandWithStats, BrandWithProducts, BrandStats, BrandPopular,
    BrandList, BrandFilter, BrandSort, BrandBulkUpdate,
    BrandImport, BrandExport, BrandAnalytics
)

# Store schemas
from app.schemas.store import (
    StoreBase, StoreCreate, StoreUpdate, StoreResponse, StoreSimple,
    StoreWithOwner, StoreWithStats, StoreFull, StoreList, StoreFilter, StoreSort,
    StoreStatus, VerificationStatus, BusinessType
)

# Order schemas
from app.schemas.order import (
    OrderBase, OrderCreate, OrderUpdate, OrderResponse, OrderSimple,
    OrderWithItems, OrderWithPayments, OrderWithShipments, OrderFull,
    OrderFinancials, OrderTimeline, OrderStatusUpdate, OrderList, OrderFilter,
    OrderItemBase, OrderItemCreate, OrderItemResponse, OrderItemSimple,
    PaymentBase, PaymentCreate, PaymentResponse, PaymentSimple,
    OrderShipmentBase, OrderShipmentCreate, OrderShipmentUpdate, OrderShipmentResponse,
    OrderCancel, OrderRefund, OrderConfirm, OrderShip,
    OrderAnalytics, OrderMetrics, OrderTrends,
    OrderStatus, PaymentStatus, FulfillmentStatus, PaymentMethod, ShipmentStatus
)

# Review schemas
from app.schemas.review import (
    ReviewBase, ReviewCreate, ReviewUpdate, ReviewResponse, ReviewSimple,
    ReviewWithUser, ReviewWithProduct, ReviewWithVotes, ReviewFull,
    ReviewList, ReviewFilter, ReviewVoteBase, ReviewVoteCreate,
    ReviewVoteUpdate, ReviewVoteResponse, RatingSummary,
    ProductReviewStats, UserReviewStats, ReviewAnalytics, ReviewTrends,
    ReviewStatus
)

# Cart schemas
from app.schemas.cart import (
    CartBase, CartCreate, CartUpdate, CartResponse, CartSimple,
    CartWithItems, CartWithUser, CartItemBase,
    CartItemCreate, CartItemUpdate, CartItemResponse, CartItemSimple,
    CartList, CartFilter, CartItemFilter, CartAddItem, CartUpdateItem,
    CartRemoveItem, CartBulkUpdate, CartMerge, CartAnalytics,
    AbandonedCartAnalytics, CartRecoveryEmail
)

# Wishlist schemas
from app.schemas.wishlist import (
    WishlistBase, WishlistCreate, WishlistUpdate, WishlistResponse,
    WishlistSimple, WishlistWithItems, WishlistWithUser, WishlistStats,
    WishlistList, WishlistFilter, WishlistItemBase, WishlistItemCreate,
    WishlistItemResponse, WishlistItemSimple, WishlistItemFilter,
    WishlistAddItem, WishlistRemoveItem, WishlistBulkAction,
    WishlistAnalytics, WishlistNotification
)

# Conversation schemas
from app.schemas.conversation import (
    ConversationBase, ConversationCreate, ConversationUpdate, ConversationResponse,
    ConversationSimple, ConversationWithParticipants, ConversationWithLastMessage,
    ConversationFull, ConversationStats, ConversationList, ConversationFilterSchema,
    MessageBase, MessageCreate, MessageUpdate, MessageResponse, MessageSimple,
    MessageWithSender, MessageList,
    ConversationAnalytics, ConversationTrends,
    ConversationStatus, ConversationPriority, MessageType
)

# Notification schemas
from app.schemas.notification import (
    NotificationBase, NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationSimple, NotificationWithUser, NotificationSummary,
    NotificationList, NotificationFilterSchema, NotificationSettings,
    NotificationPreferences, NotificationAnalytics,
    NotificationType, NotificationUrgency, NotificationStatus
)

# Discount schemas
from app.schemas.discount import (
    DiscountCodeBase, DiscountCodeCreate, DiscountCodeUpdate, DiscountCodeResponse,
    DiscountCodeSimple, DiscountCodeWithUsages,
    DiscountCodeList, DiscountCodeFilter, DiscountUsageBase,
    DiscountUsageCreate, DiscountUsageResponse, DiscountUsageSimple,
    DiscountApply, DiscountApplyResult, DiscountCalculation,
    DiscountType
)

# Analytics schemas
from app.schemas.analytics import (
    ProductViewBase, ProductViewCreate, ProductViewResponse, ProductViewSimple,
    ProductViewWithProduct, ProductViewWithUser, ProductViewStats,
    ProductViewList, ProductViewFilter, SearchLogBase, SearchLogCreate,
    SearchLogResponse, SearchLogSimple, SearchLogWithUser, SearchLogStats,
    PopularSearchTerm, SearchLogList, SearchLogFilter,
    DailyAnalytics, HourlyAnalytics, UserBehaviorAnalytics,
    ProductAnalytics, TrendingProduct, SearchTrend,
    ViewerType, BrowserType, DeviceType
)

# Экспорт всех схем
__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserCreateAdmin", "UserUpdate", "UserUpdateRole",
    "UserUpdateStatus", "UserResponse", "UserSimple", "UserWithProfile", "UserWithAddresses",
    "UserProfileBase", "UserProfileCreate", "UserProfileUpdate", "UserProfileResponse",
    "UserAddressBase", "UserAddressCreate", "UserAddressUpdate", "UserAddressResponse",
    "UserLogin", "Token", "TokenData", "PasswordChange", "PasswordReset", "PasswordResetConfirm",
    "UserRole", "UserStatus", "AddressType",
    
    # Product schemas
    "ProductBase", "ProductCreate", "ProductUpdate", "ProductResponse", "ProductSimple",
    "ProductWithDetails", "ProductWithVariants", "ProductList", "ProductFilter", "ProductSort",
    "ProductVariantBase", "ProductVariantCreate", "ProductVariantUpdate", "ProductVariantResponse",
    "ProductVariantWithImages", "ProductImageBase", "ProductImageCreate", "ProductImageUpdate",
    "ProductImageResponse", "ProductStatus", "ProductVisibility",
    
    # Category schemas
    "CategoryBase", "CategoryCreate", "CategoryUpdate", "CategoryResponse", "CategorySimple",
    "CategoryWithChildren", "CategoryWithProducts", "CategoryTree", "CategoryList",
    "CategoryFilter", "CategorySort", "CategoryStats", "CategoryAnalytics",
    
    # Brand schemas
    "BrandBase", "BrandCreate", "BrandUpdate", "BrandResponse", "BrandSimple",
    "BrandWithStats", "BrandWithProducts", "BrandStats", "BrandPopular",
    "BrandList", "BrandFilter", "BrandSort", "BrandBulkUpdate",
    "BrandImport", "BrandExport", "BrandAnalytics",
    
    # Store schemas
    "StoreBase", "StoreCreate", "StoreUpdate", "StoreResponse", "StoreSimple",
    "StoreWithOwner", "StoreWithProducts", "StoreWithStats", "StoreFull",
    "StoreStats", "StoreList", "StoreFilter", "StoreSort",
    "StoreStatus", "VerificationStatus", "BusinessType",
    
    # Order schemas
    "OrderBase", "OrderCreate", "OrderUpdate", "OrderResponse", "OrderSimple",
    "OrderWithItems", "OrderWithPayments", "OrderWithShipments", "OrderFull",
    "OrderFinancials", "OrderTimeline", "OrderStatusUpdate", "OrderList", "OrderFilter",
    "OrderItemBase", "OrderItemCreate", "OrderItemResponse", "OrderItemSimple",
    "PaymentBase", "PaymentCreate", "PaymentResponse", "PaymentSimple",
    "OrderShipmentBase", "OrderShipmentCreate", "OrderShipmentUpdate", "OrderShipmentResponse",
    "OrderCancel", "OrderRefund", "OrderConfirm", "OrderShip",
    "OrderAnalytics", "OrderMetrics", "OrderTrends",
    "OrderStatus", "PaymentStatus", "FulfillmentStatus", "PaymentMethod", "ShipmentStatus",
    
    # Review schemas
    "ReviewBase", "ReviewCreate", "ReviewUpdate", "ReviewResponse", "ReviewSimple",
    "ReviewWithUser", "ReviewWithProduct", "ReviewWithVotes", "ReviewFull",
    "ReviewList", "ReviewFilter", "ReviewVoteBase", "ReviewVoteCreate",
    "ReviewVoteUpdate", "ReviewVoteResponse", "RatingSummary",
    "ProductReviewStats", "UserReviewStats", "ReviewAnalytics", "ReviewTrends",
    "ReviewStatus",
    
    # Cart schemas
    "CartBase", "CartCreate", "CartUpdate", "CartResponse", "CartSimple",
    "CartWithItems", "CartWithUser", "CartFull", "CartItemBase",
    "CartItemCreate", "CartItemUpdate", "CartItemResponse", "CartItemSimple",
    "CartList", "CartFilter", "CartItemFilter", "CartAddItem", "CartUpdateItem",
    "CartRemoveItem", "CartBulkUpdate", "CartMerge", "CartAnalytics",
    "AbandonedCartAnalytics", "CartRecoveryEmail",
    
    # Wishlist schemas
    "WishlistBase", "WishlistCreate", "WishlistUpdate", "WishlistResponse",
    "WishlistSimple", "WishlistWithItems", "WishlistWithUser", "WishlistStats",
    "WishlistList", "WishlistFilter", "WishlistItemBase", "WishlistItemCreate",
    "WishlistItemResponse", "WishlistItemSimple", "WishlistItemFilter",
    "WishlistAddItem", "WishlistRemoveItem", "WishlistBulkAction",
    "WishlistAnalytics", "WishlistNotification",
    
    # Conversation schemas
    "ConversationBase", "ConversationCreate", "ConversationUpdate", "ConversationResponse",
    "ConversationSimple", "ConversationWithParticipants", "ConversationWithLastMessage",
    "ConversationFull", "ConversationStats", "ConversationList", "ConversationFilterSchema",
    "MessageBase", "MessageCreate", "MessageUpdate", "MessageResponse", "MessageSimple",
    "MessageWithSender", "MessageList", "MessageFilter",
    "ConversationAnalytics", "ConversationTrends",
    "ConversationStatus", "ConversationPriority", "MessageType",
    
    # Notification schemas
    "NotificationBase", "NotificationCreate", "NotificationUpdate", "NotificationResponse",
    "NotificationSimple", "NotificationWithUser", "NotificationSummary",
    "NotificationList", "NotificationFilterSchema", "NotificationSettings",
    "NotificationPreferences", "NotificationAnalytics",
    "NotificationType", "NotificationUrgency", "NotificationStatus",
    
    # Discount schemas
    "DiscountCodeBase", "DiscountCodeCreate", "DiscountCodeUpdate", "DiscountCodeResponse",
    "DiscountCodeSimple", "DiscountCodeWithUsages", "DiscountCodeAnalytics",
    "DiscountCodeList", "DiscountCodeFilter", "DiscountUsageBase",
    "DiscountUsageCreate", "DiscountUsageResponse", "DiscountUsageSimple",
    "DiscountApply", "DiscountApplyResult", "DiscountCalculation",
    "DiscountType",
    
    # Analytics schemas
    "ProductViewBase", "ProductViewCreate", "ProductViewResponse", "ProductViewSimple",
    "ProductViewWithProduct", "ProductViewWithUser", "ProductViewStats",
    "ProductViewList", "ProductViewFilter", "SearchLogBase", "SearchLogCreate",
    "SearchLogResponse", "SearchLogSimple", "SearchLogWithUser", "SearchLogStats",
    "PopularSearchTerm", "SearchLogList", "SearchLogFilter",
    "DailyAnalytics", "HourlyAnalytics", "UserBehaviorAnalytics",
    "ProductAnalytics", "TrendingProduct", "SearchTrend",
    "ViewerType", "BrowserType", "DeviceType",
]