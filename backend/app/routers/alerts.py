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
    """Get alerts from MySQL with item details."""
    return crud.get_alerts(db, skip=skip, limit=limit, acknowledged=acknowledged)


@router.get("/mongo")
def list_mongo_alerts(skip: int = 0, limit: int = 100):
    """
    Get alerts from MongoDB.
    Demonstrates NoSQL integration for log data.
    """
    alerts = get_mongo_alerts(limit=limit, skip=skip)
    total = get_mongo_alert_count()
    
    return {
        "total": total,
        "count": len(alerts),
        "alerts": alerts
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
