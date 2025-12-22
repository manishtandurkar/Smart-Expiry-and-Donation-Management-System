"""
API Router for Alert endpoints with MongoDB integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas
from ..database import get_db, get_mongo_db
from ..tasks import run_expiry_check, get_mongo_alerts, get_mongo_alert_count
from pymongo.database import Database

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("", response_model=List[schemas.AlertWithItem])
def list_alerts(
    skip: int = 0,
    limit: int = 100,
    acknowledged: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get alerts from MySQL with item details. Only shows alerts for items in inventory (quantity > 0)."""
    alerts = crud.get_alerts(db, skip=skip, limit=limit, acknowledged=acknowledged)
    # Additional filter to ensure item has quantity > 0
    return [alert for alert in alerts if alert.item and alert.item.quantity > 0]


@router.get("/mongo")
def list_mongo_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get alerts from MongoDB, filtered by current inventory status.
    Only returns alerts for items that still have quantity > 0.
    """
    from ..models import Item
    
    alerts = get_mongo_alerts(limit=limit, skip=skip)
    
    # Filter alerts to only include items currently in inventory
    filtered_alerts = []
    for alert in alerts:
        item_id = alert.get('item_id')
        if item_id:
            # Check if item still exists and has quantity > 0
            item = db.query(Item).filter(Item.item_id == item_id).first()
            if item and item.quantity > 0:
                filtered_alerts.append(alert)
    
    return {
        "total": len(filtered_alerts),
        "count": len(filtered_alerts),
        "alerts": filtered_alerts
    }


@router.post("/check", response_model=schemas.MessageResponse)
def trigger_expiry_check(days: Optional[int] = None):
    """
    Manually trigger expiry check.
    Creates alerts in both MySQL and MongoDB.
    Demonstrates dual-database write operations.
    """
    result = run_expiry_check(days)
    
    return schemas.MessageResponse(
        message="Expiry check completed",
        success=True,
        data=result
    )


@router.put("/{alert_id}/acknowledge", response_model=schemas.AlertResponse)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Mark alert as acknowledged."""
    alert = crud.acknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
