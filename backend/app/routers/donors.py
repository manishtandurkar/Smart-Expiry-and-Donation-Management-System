"""
API Router for Donor endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db
from ..deps import verify_admin

router = APIRouter(prefix="/api/donors", tags=["Donors"])


@router.get("", response_model=List[schemas.DonorResponse])
def list_donors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of all donors."""
    return crud.get_donors(db, skip=skip, limit=limit)


@router.get("/{donor_id}", response_model=schemas.DonorResponse)
def get_donor(donor_id: int, db: Session = Depends(get_db)):
    """Get donor by ID."""
    donor = crud.get_donor(db, donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    return donor


@router.post("", response_model=schemas.DonorResponse, status_code=status.HTTP_201_CREATED)
def create_donor(donor: schemas.DonorCreate, db: Session = Depends(get_db)):
    """Create new donor."""
    return crud.create_donor(db, donor)


@router.put("/{donor_id}", response_model=schemas.DonorResponse)
def update_donor(donor_id: int, donor: schemas.DonorUpdate, db: Session = Depends(get_db)):
    """Update donor information."""
    updated = crud.update_donor(db, donor_id, donor)
    if not updated:
        raise HTTPException(status_code=404, detail="Donor not found")
    return updated


@router.delete("/{donor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_donor(donor_id: int, db: Session = Depends(get_db), _admin=Depends(verify_admin)):
    """Delete donor (admin only)."""
    deleted = crud.delete_donor(db, donor_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Donor not found")
    return None
