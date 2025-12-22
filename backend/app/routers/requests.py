"""
Donation Requests Router
Handles donation requests from receivers for admin approval
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from ..deps import get_db
from .. import crud, schemas, models

router = APIRouter(
    prefix="/api/requests",
    tags=["Donation Requests"]
)


@router.get("/", response_model=List[schemas.DonationRequestResponse])
def get_all_requests(
    status: Optional[str] = None,
    receiver_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all donation requests with optional filters
    """
    return crud.get_donation_requests(db, status=status, receiver_id=receiver_id, skip=skip, limit=limit)


@router.get("/receiver/{receiver_id}", response_model=List[schemas.DonationRequestResponse])
def get_receiver_requests(
    receiver_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all requests for a specific receiver
    """
    return crud.get_donation_requests(db, receiver_id=receiver_id, status=status)


@router.get("/approved/{receiver_id}", response_model=List[schemas.DonationRequestResponse])
def get_approved_requests(
    receiver_id: int,
    db: Session = Depends(get_db)
):
    """
    Get approved requests for a receiver (items they can claim)
    """
    return crud.get_donation_requests(db, receiver_id=receiver_id, status="approved")


@router.post("/", response_model=schemas.DonationRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    request_data: schemas.DonationRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new donation request
    """
    # Validate receiver exists
    receiver = crud.get_receiver(db, request_data.receiver_id)
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )
    
    # If requesting existing item, validate it exists and has quantity
    if request_data.request_type == schemas.RequestType.EXISTING:
        if not request_data.item_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="item_id is required for existing item requests"
            )
        item = crud.get_item(db, request_data.item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        if item.quantity < request_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({request_data.quantity}) exceeds available ({item.quantity})"
            )
    else:
        # For new item requests, item_name is required
        if not request_data.item_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="item_name is required for new item requests"
            )
    
    return crud.create_donation_request(db, request_data)


@router.put("/{request_id}", response_model=schemas.DonationRequestResponse)
def update_request_status(
    request_id: int,
    update_data: schemas.DonationRequestUpdate,
    db: Session = Depends(get_db)
):
    """
    Update request status (admin only)
    When approved, creates the donation record and updates inventory
    """
    request = crud.get_donation_request(db, request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # If approving an existing item request, create the donation
    if update_data.status == schemas.RequestStatus.APPROVED and request.request_type == 'existing':
        item = crud.get_item(db, request.item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item no longer exists"
            )
        if item.quantity < request.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient quantity. Available: {item.quantity}"
            )
        
        # Create donation record
        donation_data = schemas.DonationCreate(
            item_id=request.item_id,
            receiver_id=request.receiver_id,
            quantity=request.quantity,
            notes=f"Approved request #{request_id}"
        )
        crud.create_donation(db, donation_data)
    
    return crud.update_donation_request(db, request_id, update_data)


@router.delete("/{request_id}")
def delete_request(request_id: int, db: Session = Depends(get_db)):
    """
    Delete a donation request (only pending requests can be deleted)
    """
    request = crud.get_donation_request(db, request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    if request.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending requests can be deleted"
        )
    
    success = crud.delete_donation_request(db, request_id)
    return {"message": "Request deleted successfully"}
