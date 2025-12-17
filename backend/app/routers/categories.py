"""
API Router for Category endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("", response_model=List[schemas.CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """Get list of all categories."""
    return crud.get_categories(db)


@router.get("/{category_id}", response_model=schemas.CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get category by ID."""
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """Create new category."""
    return crud.create_category(db, category)
