"""
API Router for Item endpoints with NLP integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas
from ..database import get_db
from ..nlp import predict_item_category

router = APIRouter(prefix="/api/items", tags=["Items"])


@router.get("", response_model=List[schemas.ItemResponse])
def list_items(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    donor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of all items with optional filters."""
    return crud.get_items(db, skip=skip, limit=limit, category_id=category_id, donor_id=donor_id)


@router.get("/expiring", response_model=List[schemas.ItemResponse])
def get_expiring_items(days: int = 30, db: Session = Depends(get_db)):
    """Get items expiring within specified days."""
    return crud.get_expiring_items(db, days=days)


@router.get("/expired", response_model=List[schemas.ItemResponse])
def get_expired_items(db: Session = Depends(get_db)):
    """Get expired items."""
    return crud.get_expired_items(db)


@router.get("/{item_id}", response_model=schemas.ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get item by ID."""
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """
    Create new item with NLP category prediction.
    Predicts category automatically using the item name (primary signal).
    """
    # NLP: Predict category from item name if category not provided
    if not item.category_id:
        categories = crud.get_categories(db)
        category_names = [c.category_name for c in categories]

        # Use name as the main signal; fall back to description if name missing
        text_for_prediction = item.name or item.description or ""
        predicted_name, confidence = predict_item_category(text_for_prediction, category_names)

        # Find category ID
        for cat in categories:
            if cat.category_name == predicted_name:
                item.category_id = cat.category_id
                break
    
    return crud.create_item(db, item)


@router.post("/predict-category", response_model=schemas.NLPPrediction)
def predict_category(name: str, db: Session = Depends(get_db)):
    """
    NLP endpoint: Predict category from item name (primary signal).
    """
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Item name is required")
    
    categories = crud.get_categories(db)
    category_names = [c.category_name for c in categories]
    
    predicted_name, confidence = predict_item_category(name, category_names)
    
    return schemas.NLPPrediction(
        description=name,
        predicted_category=predicted_name,
        confidence=confidence,
        available_categories=category_names
    )


@router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    """Update item information."""
    updated = crud.update_item(db, item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated
