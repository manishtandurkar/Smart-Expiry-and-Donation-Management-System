"""
Background tasks for expiry checking and alert generation.
Implements dual-database logging (MySQL + MongoDB).
"""

from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from pymongo.database import Database
from typing import List, Dict
from . import models, schemas
from .database import SessionLocal, mongo_db
from .config import settings
import logging

logger = logging.getLogger(__name__)


class ExpiryChecker:
    """
    Handles expiry checking and alert generation.
    Demonstrates dual-database operations (MySQL + MongoDB).
    """
    
    def __init__(self, db: Session, mongo: Database):
        """
        Initialize expiry checker.
        
        Args:
            db: MySQL database session
            mongo: MongoDB database instance
        """
        self.db = db
        self.mongo = mongo
    
    def get_expiring_items(self, days_threshold: int = None) -> List[models.Item]:
        """
        Get items expiring within threshold days.
        
        Args:
            days_threshold: Number of days to look ahead
            
        Returns:
            List of items expiring soon
        """
        if days_threshold is None:
            days_threshold = settings.EXPIRY_CHECK_DAYS
        
        threshold_date = date.today() + timedelta(days=days_threshold)
        
        items = self.db.query(models.Item).filter(
            models.Item.expiry_date <= threshold_date,
            models.Item.expiry_date >= date.today(),
            models.Item.quantity > 0
        ).all()
        
        return items
    
    def calculate_severity(self, days_until_expiry: int) -> str:
        """
        Calculate alert severity based on days until expiry.
        
        Args:
            days_until_expiry: Number of days until item expires
            
        Returns:
            Severity level (CRITICAL, HIGH, MEDIUM, LOW)
        """
        if days_until_expiry <= 3:
            return "CRITICAL"
        elif days_until_expiry <= 7:
            return "HIGH"
        elif days_until_expiry <= 14:
            return "MEDIUM"
        else:
            return "LOW"
    
    def alert_exists_today(self, item_id: int) -> bool:
        """
        Check if alert already exists for item today.
        
        Args:
            item_id: Item ID to check
            
        Returns:
            True if alert exists, False otherwise
        """
        exists = self.db.query(models.Alert).filter(
            models.Alert.item_id == item_id,
            models.Alert.alert_date == date.today()
        ).first()
        
        return exists is not None
    
    def create_mysql_alert(self, item: models.Item) -> models.Alert:
        """
        Create alert in MySQL database.
        
        Args:
            item: Item object
            
        Returns:
            Created alert object
        """
        days_remaining = item.days_until_expiry
        severity = self.calculate_severity(days_remaining)
        
        message = (
            f"Item '{item.name}' (ID: {item.item_id}) expires in {days_remaining} days. "
            f"Current quantity: {item.quantity}. "
            f"Action required: Prioritize for donation."
        )
        
        alert = models.Alert(
            item_id=item.item_id,
            message=message,
            severity=severity,
            alert_date=date.today()
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def create_mongo_alert(self, item: models.Item, alert: models.Alert) -> Dict:
        """
        Create alert document in MongoDB.
        
        Args:
            item: Item object
            alert: Alert object from MySQL
            
        Returns:
            MongoDB document or None if MongoDB unavailable
        """
        if self.mongo is None:
            return None
            
        document = {
            'alert_id': alert.alert_id,
            'item_id': item.item_id,
            'item_name': item.name,
            'message': alert.message,
            'alert_date': alert.alert_date.isoformat(),
            'severity': alert.severity,
            'days_until_expiry': item.days_until_expiry,
            'quantity': item.quantity,
            'category_id': item.category_id,
            'category_name': item.category.category_name,
            'donor_id': item.donor_id,
            'donor_name': item.donor.name,
            'expiry_date': item.expiry_date.isoformat(),
            'timestamp': datetime.utcnow(),
            'is_acknowledged': False
        }
        
        try:
            result = self.mongo.alerts.insert_one(document)
            document['_id'] = str(result.inserted_id)
            return document
        except Exception as e:
            print(f"⚠ Failed to create MongoDB alert: {str(e)}")
            return None
    
    def generate_alerts(self, days_threshold: int = None) -> Dict[str, any]:
        """
        Generate expiry alerts for items expiring soon.
        Implements dual-database logging (MySQL + MongoDB).
        
        Args:
            days_threshold: Days to look ahead (default from settings)
            
        Returns:
            Dictionary with generation statistics
        """
        expiring_items = self.get_expiring_items(days_threshold)
        
        mysql_alerts_created = 0
        mongo_alerts_created = 0
        skipped = 0
        
        for item in expiring_items:
            # Skip if alert already exists today
            if self.alert_exists_today(item.item_id):
                skipped += 1
                continue
            
            try:
                # Create MySQL alert
                mysql_alert = self.create_mysql_alert(item)
                mysql_alerts_created += 1
                
                # Create MongoDB alert
                self.create_mongo_alert(item, mysql_alert)
                mongo_alerts_created += 1
                
                logger.info(f"Alert created for item {item.item_id}: {item.name}")
                
            except Exception as e:
                logger.error(f"Error creating alert for item {item.item_id}: {str(e)}")
                continue
        
        result = {
            'checked_items': len(expiring_items),
            'mysql_alerts_created': mysql_alerts_created,
            'mongo_alerts_created': mongo_alerts_created,
            'skipped': skipped,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Alert generation completed: {result}")
        return result
    
    def get_expired_items(self) -> List[models.Item]:
        """
        Get items that have already expired.
        
        Returns:
            List of expired items
        """
        items = self.db.query(models.Item).filter(
            models.Item.expiry_date < date.today(),
            models.Item.quantity > 0
        ).all()
        
        return items
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """
        Mark alert as acknowledged in both databases.
        
        Args:
            alert_id: Alert ID to acknowledge
            
        Returns:
            True if successful
        """
        try:
            # Update MySQL
            alert = self.db.query(models.Alert).filter(
                models.Alert.alert_id == alert_id
            ).first()
            
            if alert:
                alert.is_acknowledged = True
                self.db.commit()
                
                # Update MongoDB
                self.mongo.alerts.update_many(
                    {'alert_id': alert_id},
                    {'$set': {'is_acknowledged': True}}
                )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {str(e)}")
            self.db.rollback()
            return False


def run_expiry_check(days_threshold: int = None) -> Dict[str, any]:
    """
    Standalone function to run expiry check.
    Can be called from scheduled tasks or API endpoints.
    
    Args:
        days_threshold: Days to look ahead
        
    Returns:
        Generation statistics
    """
    db = SessionLocal()
    try:
        checker = ExpiryChecker(db, mongo_db)
        result = checker.generate_alerts(days_threshold)
        return result
    finally:
        db.close()


def get_mongo_alerts(limit: int = 100, skip: int = 0) -> List[Dict]:
    """
    Retrieve alerts from MongoDB.
    
    Args:
        limit: Maximum number of alerts to return
        skip: Number of alerts to skip
        
    Returns:
        List of alert documents
    """
    alerts = list(
        mongo_db.alerts
        .find()
        .sort('timestamp', -1)  # Most recent first
        .skip(skip)
        .limit(limit)
    )
    
    # Convert ObjectId to string
    for alert in alerts:
        alert['_id'] = str(alert['_id'])
    
    return alerts


def get_mongo_alert_count() -> int:
    """
    Get total count of alerts in MongoDB.
    
    Returns:
        Number of alerts
    """
    return mongo_db.alerts.count_documents({})
