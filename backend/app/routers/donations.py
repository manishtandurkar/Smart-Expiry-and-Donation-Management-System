"""
API Router for Donation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/donations", tags=["Donations"])


@router.get("", response_model=List[schemas.DonationResponse])
def list_donations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of all donations."""
    return crud.get_donations(db, skip=skip, limit=limit)


@router.post("", response_model=schemas.DonationResponse, status_code=status.HTTP_201_CREATED)
def create_donation(donation: schemas.DonationCreate, db: Session = Depends(get_db)):
    """
    Record new donation.
    Automatically updates item inventory quantity.
    Demonstrates transactional database operations.
    """
    try:
        return crud.create_donation(db, donation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating donation: {str(e)}")
