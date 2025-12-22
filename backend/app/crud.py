"""
CRUD operations for database entities.
Provides reusable database operations for all models.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, case
from typing import List, Optional
from datetime import date, timedelta
from . import models, schemas


# ============================================================================
# Donor CRUD
# ============================================================================

def get_donors(db: Session, skip: int = 0, limit: int = 100) -> List[models.Donor]:
    return db.query(models.Donor).offset(skip).limit(limit).all()


def get_donor(db: Session, donor_id: int) -> Optional[models.Donor]:
    return db.query(models.Donor).filter(models.Donor.donor_id == donor_id).first()


def create_donor(db: Session, donor: schemas.DonorCreate) -> models.Donor:
    db_donor = models.Donor(**donor.model_dump())
    db.add(db_donor)
    db.commit()
    db.refresh(db_donor)
    return db_donor


def update_donor(db: Session, donor_id: int, donor: schemas.DonorUpdate) -> Optional[models.Donor]:
    db_donor = get_donor(db, donor_id)
    if db_donor:
        update_data = donor.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_donor, key, value)
        db.commit()
        db.refresh(db_donor)
    return db_donor


def delete_donor(db: Session, donor_id: int) -> bool:
    """Delete a donor by id. Returns True if deleted."""
    db_donor = get_donor(db, donor_id)
    if not db_donor:
        return False
    db.delete(db_donor)
    db.commit()
    return True


# ============================================================================
# Item CRUD
# ============================================================================

def get_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    donor_id: Optional[int] = None
) -> List[models.Item]:
    query = db.query(models.Item).options(
        joinedload(models.Item.donor)
    )
    
    # Only show items with quantity > 0 in inventory
    query = query.filter(models.Item.quantity > 0)
    
    if category:
        query = query.filter(models.Item.category == category)
    if donor_id:
        query = query.filter(models.Item.donor_id == donor_id)
    
    return query.offset(skip).limit(limit).all()


def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    return db.query(models.Item).options(
        joinedload(models.Item.donor)
    ).filter(models.Item.item_id == item_id).first()


def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    item_data = item.model_dump(exclude={'predicted_category'})
    db_item = models.Item(**item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, item: schemas.ItemUpdate) -> Optional[models.Item]:
    db_item = get_item(db, item_id)
    if db_item:
        update_data = item.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item


def get_expiring_items(db: Session, days: int = 30) -> List[models.Item]:
    """Get items expiring within specified days."""
    threshold_date = date.today() + timedelta(days=days)
    return db.query(models.Item).options(
        joinedload(models.Item.donor)
    ).filter(
        and_(
            models.Item.expiry_date <= threshold_date,
            models.Item.expiry_date >= date.today(),
            models.Item.quantity > 0
        )
    ).all()


def get_expired_items(db: Session) -> List[models.Item]:
    """Get expired items."""
    return db.query(models.Item).options(
        joinedload(models.Item.donor)
    ).filter(
        and_(
            models.Item.expiry_date < date.today(),
            models.Item.quantity > 0
        )
    ).all()


# ============================================================================
# Receiver CRUD
# ============================================================================

def get_receivers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Receiver]:
    return db.query(models.Receiver).offset(skip).limit(limit).all()


def get_receiver(db: Session, receiver_id: int) -> Optional[models.Receiver]:
    return db.query(models.Receiver).filter(models.Receiver.receiver_id == receiver_id).first()


def create_receiver(db: Session, receiver: schemas.ReceiverCreate) -> models.Receiver:
    db_receiver = models.Receiver(**receiver.model_dump())
    db.add(db_receiver)
    db.commit()
    db.refresh(db_receiver)
    return db_receiver


def delete_receiver(db: Session, receiver_id: int) -> bool:
    """Delete a receiver by id. Returns True if deleted."""
    db_receiver = get_receiver(db, receiver_id)
    if not db_receiver:
        return False
    db.delete(db_receiver)
    db.commit()
    return True


# ============================================================================
# Donation CRUD
# ============================================================================

def get_donations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Donation]:
    return db.query(models.Donation).options(
        joinedload(models.Donation.item).joinedload(models.Item.donor),
        joinedload(models.Donation.receiver),
        joinedload(models.Donation.approving_donor)
    ).order_by(models.Donation.created_at.desc()).offset(skip).limit(limit).all()


def create_donation(db: Session, donation: schemas.DonationCreate) -> models.Donation:
    """
    Create donation and update item quantity.
    Implements transaction to ensure data consistency.
    """
    # Check item exists and has sufficient quantity
    item = get_item(db, donation.item_id)
    if not item:
        raise ValueError(f"Item {donation.item_id} not found")
    
    if item.quantity < donation.quantity:
        raise ValueError(f"Insufficient quantity. Available: {item.quantity}, Requested: {donation.quantity}")
    
    # Create donation
    db_donation = models.Donation(**donation.model_dump())
    db.add(db_donation)
    
    # Update item quantity
    item.quantity -= donation.quantity
    
    # Commit transaction
    db.commit()
    db.refresh(db_donation)
    
    # Reload with relationships for response validation
    db_donation = db.query(models.Donation).options(
        joinedload(models.Donation.item).joinedload(models.Item.donor),
        joinedload(models.Donation.receiver),
        joinedload(models.Donation.approving_donor)
    ).filter(models.Donation.donation_id == db_donation.donation_id).first()
    
    return db_donation


# ============================================================================
# Alert CRUD
# ============================================================================

def get_alerts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    acknowledged: Optional[bool] = None
) -> List[models.Alert]:
    query = db.query(models.Alert).options(
        joinedload(models.Alert.item).joinedload(models.Item.donor)
    )

    # Only include alerts for items that still have quantity > 0
    query = query.join(models.Item).filter(models.Item.quantity > 0)

    # Filter by acknowledged flag if provided
    if acknowledged is not None:
        query = query.filter(models.Alert.is_acknowledged == acknowledged)

    # Keep only CRITICAL and HIGH severities and order CRITICAL first
    query = query.filter(models.Alert.severity.in_(['CRITICAL', 'HIGH']))
    severity_rank = case(
        (models.Alert.severity == 'CRITICAL', 1),
        (models.Alert.severity == 'HIGH', 2),
        else_=3
    )

    return query.order_by(severity_rank, models.Alert.created_at.desc()).offset(skip).limit(limit).all()


def acknowledge_alert(db: Session, alert_id: int) -> Optional[models.Alert]:
    """Mark alert as acknowledged."""
    alert = db.query(models.Alert).filter(models.Alert.alert_id == alert_id).first()
    if alert:
        alert.is_acknowledged = True
        db.commit()
        db.refresh(alert)
    return alert


# ============================================================================
# Statistics
# ============================================================================

def get_dashboard_stats(db: Session) -> schemas.DashboardStats:
    """Get dashboard statistics."""
    total_items = db.query(func.count(models.Item.item_id)).scalar()
    total_donors = db.query(func.count(models.Donor.donor_id)).scalar()
    total_receivers = db.query(func.count(models.Receiver.receiver_id)).scalar()
    total_donations = db.query(func.count(models.Donation.donation_id)).scalar()
    total_alerts = db.query(func.count(models.Alert.alert_id)).filter(
        models.Alert.is_acknowledged == False
    ).scalar()
    
    threshold_date = date.today() + timedelta(days=7)
    expiring_soon = db.query(func.count(models.Item.item_id)).filter(
        and_(
            models.Item.expiry_date <= threshold_date,
            models.Item.expiry_date >= date.today(),
            models.Item.quantity > 0
        )
    ).scalar()
    
    expired_items = db.query(func.count(models.Item.item_id)).filter(
        and_(
            models.Item.expiry_date < date.today(),
            models.Item.quantity > 0
        )
    ).scalar()
    
    low_stock_items = db.query(func.count(models.Item.item_id)).filter(
        and_(
            models.Item.quantity <= 10,
            models.Item.quantity > 0
        )
    ).scalar()
    
    return schemas.DashboardStats(
        total_items=total_items or 0,
        total_donors=total_donors or 0,
        total_receivers=total_receivers or 0,
        total_donations=total_donations or 0,
        total_alerts=total_alerts or 0,
        expiring_soon=expiring_soon or 0,
        expired_items=expired_items or 0,
        low_stock_items=low_stock_items or 0
    )


# ============================================================================
# User CRUD
# ============================================================================

def get_users(db: Session, role: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[models.User]:
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    return query.offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


def get_donor_by_user_id(db: Session, user_id: int) -> Optional[models.Donor]:
    return db.query(models.Donor).filter(models.Donor.user_id == user_id).first()


def get_receiver_by_user_id(db: Session, user_id: int) -> Optional[models.Receiver]:
    return db.query(models.Receiver).filter(models.Receiver.user_id == user_id).first()


def create_donor_with_user(db: Session, donor: schemas.DonorCreate, user_id: int) -> models.Donor:
    db_donor = models.Donor(**donor.model_dump(), user_id=user_id)
    db.add(db_donor)
    db.commit()
    db.refresh(db_donor)
    return db_donor


def create_receiver_with_user(db: Session, receiver: schemas.ReceiverCreate, user_id: int) -> models.Receiver:
    db_receiver = models.Receiver(**receiver.model_dump(), user_id=user_id)
    db.add(db_receiver)
    db.commit()
    db.refresh(db_receiver)
    return db_receiver


# ============================================================================
# Donation Request CRUD
# ============================================================================

def get_donation_requests(
    db: Session,
    status: Optional[str] = None,
    receiver_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.DonationRequest]:
    query = db.query(models.DonationRequest).options(
        joinedload(models.DonationRequest.receiver),
        joinedload(models.DonationRequest.item)
    )
    
    if status:
        query = query.filter(models.DonationRequest.status == status)
    if receiver_id:
        query = query.filter(models.DonationRequest.receiver_id == receiver_id)
    
    return query.order_by(models.DonationRequest.created_at.desc()).offset(skip).limit(limit).all()


def get_donation_request(db: Session, request_id: int) -> Optional[models.DonationRequest]:
    return db.query(models.DonationRequest).options(
        joinedload(models.DonationRequest.receiver),
        joinedload(models.DonationRequest.item)
    ).filter(models.DonationRequest.request_id == request_id).first()


def create_donation_request(db: Session, request: schemas.DonationRequestCreate) -> models.DonationRequest:
    db_request = models.DonationRequest(**request.model_dump())
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Reload with relationships
    return get_donation_request(db, db_request.request_id)


def update_donation_request(
    db: Session,
    request_id: int,
    update_data: schemas.DonationRequestUpdate
) -> Optional[models.DonationRequest]:
    db_request = db.query(models.DonationRequest).filter(
        models.DonationRequest.request_id == request_id
    ).first()
    
    if db_request:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(db_request, key, value)
        db.commit()
        db.refresh(db_request)
        return get_donation_request(db, request_id)
    return None


def delete_donation_request(db: Session, request_id: int) -> bool:
    db_request = db.query(models.DonationRequest).filter(
        models.DonationRequest.request_id == request_id
    ).first()
    if not db_request:
        return False
    db.delete(db_request)
    db.commit()
    return True
