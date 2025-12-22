"""
SQLAlchemy ORM models for MySQL database.
Maps Python classes to database tables with relationships.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, ForeignKey,
    CheckConstraint, Enum, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from .database import Base


class Donor(Base):
    """
    Donor model - Stores information about donors.
    Relationship: One Donor can donate Many Items (1-M)
    """
    __tablename__ = "Donor"
    
    donor_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(15), nullable=False, unique=True)
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship: One donor can have multiple items
    items = relationship("Item", back_populates="donor")
    # Relationship: One donor can approve multiple donations
    approved_donations = relationship("Donation", back_populates="approving_donor")
    
    def __repr__(self):
        return f"<Donor(id={self.donor_id}, name='{self.name}')>"


class Item(Base):
    """
    Item model - Inventory items with expiry tracking.
    Relationships:
        - Many Items belong to One Donor (M-1)
        - One Item can have Many Alerts (1-M)
        - One Item can have Many Donations (1-M)
    """
    __tablename__ = "Item"
    
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    expiry_date = Column(Date, nullable=False)
    description = Column(Text)
    storage_condition = Column(String(100))
    category = Column(String(50))
    donor_id = Column(Integer, ForeignKey('Donor.donor_id', ondelete='RESTRICT'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='chk_quantity'),
    )
    
    # Relationships
    donor = relationship("Donor", back_populates="items")
    alerts = relationship("Alert", back_populates="item", cascade="all, delete-orphan")
    donations = relationship("Donation", back_populates="item")
    
    def __repr__(self):
        return f"<Item(id={self.item_id}, name='{self.name}', qty={self.quantity})>"
    
    @property
    def days_until_expiry(self) -> int:
        """Calculate days remaining until expiry."""
        if isinstance(self.expiry_date, date):
            delta = self.expiry_date - date.today()
            return delta.days
        return 0
    
    @property
    def is_expired(self) -> bool:
        """Check if item is expired."""
        return self.days_until_expiry < 0
    
    @property
    def expiry_status(self) -> str:
        """Get expiry status category."""
        days = self.days_until_expiry
        if days < 0:
            return "EXPIRED"
        elif days <= 7:
            return "CRITICAL"
        elif days <= 30:
            return "WARNING"
        else:
            return "SAFE"


class Receiver(Base):
    """
    Receiver model - Organizations/individuals receiving donations.
    Relationship: One Receiver can have Many Donations (1-M)
    """
    __tablename__ = "Receiver"
    
    receiver_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(15), nullable=False, unique=True)
    address = Column(Text)
    region = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship: One receiver can have multiple donations
    donations = relationship("Donation", back_populates="receiver")
    
    def __repr__(self):
        return f"<Receiver(id={self.receiver_id}, name='{self.name}')>"


class Donation(Base):
    """
    Donation model - Records of donated items.
    Relationships:
        - Many Donations belong to One Item (M-1)
        - Many Donations belong to One Receiver (M-1)
        - Many Donations can be approved by One Donor (M-1)
    """
    __tablename__ = "Donation"
    
    donation_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('Item.item_id', ondelete='RESTRICT'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('Receiver.receiver_id', ondelete='RESTRICT'), nullable=False)
    donor_id = Column(Integer, ForeignKey('Donor.donor_id', ondelete='SET NULL'), nullable=True)
    quantity = Column(Integer, nullable=False)
    donation_date = Column(Date, nullable=False, default=date.today)
    delivery_mode = Column(String(50))
    delivered_by = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='chk_donation_quantity'),
    )
    
    # Relationships
    item = relationship("Item", back_populates="donations")
    receiver = relationship("Receiver", back_populates="donations")
    approving_donor = relationship("Donor", back_populates="approved_donations")
    
    def __repr__(self):
        return f"<Donation(id={self.donation_id}, item_id={self.item_id}, qty={self.quantity})>"


class Alert(Base):
    """
    Alert model - Expiry alerts for items.
    Relationship: Many Alerts belong to One Item (M-1)
    """
    __tablename__ = "Alert"
    
    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('Item.item_id', ondelete='CASCADE'), nullable=False)
    message = Column(Text, nullable=False)
    alert_date = Column(Date, nullable=False, default=date.today)
    severity = Column(
        Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severity_enum'),
        default='MEDIUM'
    )
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    item = relationship("Item", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.alert_id}, severity='{self.severity}')>"
