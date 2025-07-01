# app/models/__init__.py
from app.models.user import User, UserRole, UserStatus, AddressType, UserProfile, UserAddress
from app.models.product import Product, ProductStatus, ProductVisibility, ProductVariant, ProductImage
from app.models.store import Store, StoreStatus, VerificationStatus, BusinessType, StoreStats
from app.models.order import (
    Order, OrderStatus, PaymentStatus, FulfillmentStatus, PaymentMethod,
    OrderItem, Payment, ShippingZone, ShippingMethod, OrderShipment, ShipmentStatus
)
from app.models.category import Category
from app.models.brand import Brand
from app.models.review import Review, ReviewStatus, ReviewVote
from app.models.cart import Cart, CartItem
from app.models.wishlist import Wishlist, WishlistItem
from app.models.conversation import (
    Conversation, ConversationStatus, ConversationPriority, Message
)
from app.models.notification import Notification, NotificationType
from app.models.discount import DiscountCode, DiscountType, DiscountUsage
from app.models.analytics import ProductView

# Экспорт всех моделей
__all__ = [
    # User models
    "User", "UserRole", "UserStatus", "AddressType", "UserProfile", "UserAddress",
    
    # Product models
    "Product", "ProductStatus", "ProductVisibility", "ProductVariant", "ProductImage",
    
    # Store models
    "Store", "StoreStatus", "VerificationStatus", "BusinessType", "StoreStats",
    
    # Order models
    "Order", "OrderStatus", "PaymentStatus", "FulfillmentStatus", "PaymentMethod",
    "OrderItem", "Payment", "ShippingZone", "ShippingMethod", "OrderShipment", "ShipmentStatus",
    
    # Category and Brand
    "Category", "Brand",
    
    # Review models
    "Review", "ReviewStatus", "ReviewVote",
    
    # Cart models
    "Cart", "CartItem",
    
    # Wishlist models
    "Wishlist", "WishlistItem",
    
    # Conversation models
    "Conversation", "ConversationStatus", "ConversationPriority", "Message",
    
    # Notification models
    "Notification", "NotificationType",
    
    # Discount models
    "DiscountCode", "DiscountType", "DiscountUsage",
    
    # Analytics models
    "ProductView",
]