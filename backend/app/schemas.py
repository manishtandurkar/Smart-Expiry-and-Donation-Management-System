"""
Pydantic schemas for request/response validation.
Provides data validation and serialization for API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class SeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExpiryStatus(str, Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EXPIRED = "EXPIRED"


# ============================================================================
# Donor Schemas
# ============================================================================

class DonorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact: str = Field(..., pattern=r'^\d{10,15}$')
    address: Optional[str] = None


class DonorCreate(DonorBase):
    pass


class DonorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    contact: Optional[str] = Field(None, pattern=r'^\d{10,15}$')
    address: Optional[str] = None


class DonorResponse(DonorBase):
    donor_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Item Schemas
# ============================================================================

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0)
    expiry_date: date
    description: Optional[str] = None
    storage_condition: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    donor_id: int = Field(..., gt=0)


class ItemCreate(ItemBase):
    """Item creation with optional NLP category prediction."""
    predicted_category: Optional[str] = None  # For NLP prediction result


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, ge=0)
    expiry_date: Optional[date] = None
    description: Optional[str] = None
    storage_condition: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)


class ItemResponse(ItemBase):
    item_id: int
    created_at: datetime
    updated_at: datetime
    days_until_expiry: int
    expiry_status: str
    
    # Nested relationships
    donor: DonorResponse
    
    class Config:
        from_attributes = True


class ItemSummary(BaseModel):
    """Lightweight item summary for lists."""
    item_id: int
    name: str
    quantity: int
    expiry_date: date
    days_until_expiry: int
    expiry_status: str
    category_name: Optional[str]
    
    @classmethod
    def from_orm_item(cls, item):
        """Create ItemSummary from Item ORM model."""
        return cls(
            item_id=item.item_id,
            name=item.name,
            quantity=item.quantity,
            expiry_date=item.expiry_date,
            days_until_expiry=item.days_until_expiry,
            expiry_status=item.expiry_status,
            category_name=item.category if item.category else "Unknown"
        )
    
    class Config:
        from_attributes = True


# ============================================================================
# Receiver Schemas
# ============================================================================

class ReceiverBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact: str = Field(..., pattern=r'^\d{10,15}$')
    address: Optional[str] = None
    region: Optional[str] = Field(None, max_length=100)


class ReceiverCreate(ReceiverBase):
    pass


class ReceiverUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    contact: Optional[str] = Field(None, pattern=r'^\d{10,15}$')
    address: Optional[str] = None
    region: Optional[str] = Field(None, max_length=100)


class ReceiverResponse(ReceiverBase):
    receiver_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Donation Schemas
# ============================================================================

class DonationBase(BaseModel):
    item_id: int = Field(..., gt=0)
    receiver_id: int = Field(..., gt=0)
    donor_id: Optional[int] = Field(None, gt=0)
    quantity: int = Field(..., gt=0)
    donation_date: Optional[date] = Field(default_factory=date.today)
    delivery_mode: Optional[str] = Field(None, max_length=50)
    delivered_by: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class DonationCreate(DonationBase):
    pass


class DonationResponse(DonationBase):
    donation_id: int
    created_at: datetime
    
    # Nested relationships
    item: ItemSummary
    receiver: ReceiverResponse
    
    @validator('item', pre=True)
    def convert_item(cls, v):
        """Convert Item ORM model to ItemSummary."""
        if hasattr(v, 'category'):
            return ItemSummary.from_orm_item(v)
        return v
    
    class Config:
        from_attributes = True


# ============================================================================
# Alert Schemas
# ============================================================================

class AlertBase(BaseModel):
    item_id: int = Field(..., gt=0)
    message: str = Field(..., min_length=1)
    alert_date: Optional[date] = Field(default_factory=date.today)
    severity: SeverityEnum = SeverityEnum.MEDIUM


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    alert_id: int
    is_acknowledged: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertWithItem(AlertResponse):
    """Alert with item details."""
    item: ItemSummary

    @validator('item', pre=True)
    def convert_item(cls, v):
        if hasattr(v, 'category'):
            return ItemSummary.from_orm_item(v)
        return v
    
    class Config:
        from_attributes = True


class MongoAlertResponse(BaseModel):
    """MongoDB alert document schema."""
    item_id: int
    item_name: str
    message: str
    alert_date: str
    severity: str
    days_until_expiry: int
    quantity: int
    category_name: str
    timestamp: datetime


# ============================================================================
# Utility Schemas
# ============================================================================

class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_items: int
    total_donors: int
    total_receivers: int
    total_donations: int
    total_alerts: int
    expiring_soon: int
    expired_items: int
    low_stock_items: int


class NLPPrediction(BaseModel):
    """NLP category prediction result."""
    description: str
    predicted_category: str
    confidence: float
    available_categories: List[str]


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True
    data: Optional[dict] = None
