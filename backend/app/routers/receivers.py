"""
API Router for Receiver endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db
from ..deps import verify_admin

router = APIRouter(prefix="/api/receivers", tags=["Receivers"])


@router.get("", response_model=List[schemas.ReceiverResponse])
def list_receivers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of all receivers."""
    return crud.get_receivers(db, skip=skip, limit=limit)


@router.get("/{receiver_id}", response_model=schemas.ReceiverResponse)
def get_receiver(receiver_id: int, db: Session = Depends(get_db)):
    """Get receiver by ID."""
    receiver = crud.get_receiver(db, receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    return receiver


@router.post("", response_model=schemas.ReceiverResponse, status_code=status.HTTP_201_CREATED)
def create_receiver(receiver: schemas.ReceiverCreate, db: Session = Depends(get_db)):
    """Create new receiver."""
    return crud.create_receiver(db, receiver)


@router.delete("/{receiver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receiver(receiver_id: int, db: Session = Depends(get_db), _admin=Depends(verify_admin)):
    """Delete receiver (admin only)."""
    deleted = crud.delete_receiver(db, receiver_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Receiver not found")
    return None
