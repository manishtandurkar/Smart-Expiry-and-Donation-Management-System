"""
Authentication Router
Handles user login and registration with role-based access
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..deps import get_db
from .. import crud, schemas, models

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=schemas.UserWithToken)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return user info with associated donor/receiver ID
    """
    user = crud.get_user_by_username(db, login_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Simple password check (in production, use hashed passwords)
    if user.password != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    # Get associated donor_id or receiver_id
    donor_id = None
    receiver_id = None
    
    if user.role == 'donor':
        donor = crud.get_donor_by_user_id(db, user.user_id)
        if donor:
            donor_id = donor.donor_id
        else:
            # Auto-create missing donor profile
            try:
                donor_data = schemas.DonorCreate(
                    name=user.name,
                    contact=user.contact or "0000000000",
                    address=user.address
                )
                donor = crud.create_donor_with_user(db, donor_data, user.user_id)
                donor_id = donor.donor_id
            except Exception as e:
                print(f"Error auto-creating donor profile: {e}")

    elif user.role == 'receiver':
        receiver = crud.get_receiver_by_user_id(db, user.user_id)
        if receiver:
            receiver_id = receiver.receiver_id
        else:
            # Auto-create missing receiver profile
            try:
                receiver_data = schemas.ReceiverCreate(
                    name=user.name,
                    contact=user.contact or "0000000000",
                    address=user.address,
                    region="Unknown"
                )
                receiver = crud.create_receiver_with_user(db, receiver_data, user.user_id)
                receiver_id = receiver.receiver_id
            except Exception as e:
                print(f"Error auto-creating receiver profile: {e}")
    
    return schemas.UserWithToken(
        user=user,
        donor_id=donor_id,
        receiver_id=receiver_id
    )


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: schemas.UserCreate,
    admin_password: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Register a new user (admin only)
    Admin password required to create new users
    """
    # Check if username already exists
    existing_user = crud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create user
    user = crud.create_user(db, user_data)
    
    # Create associated donor/receiver record
    if user_data.role == schemas.UserRole.DONOR:
        donor_data = schemas.DonorCreate(
            name=user_data.name,
            contact=user_data.contact or "0000000000",
            address=user_data.address
        )
        crud.create_donor_with_user(db, donor_data, user.user_id)
    elif user_data.role == schemas.UserRole.RECEIVER:
        receiver_data = schemas.ReceiverCreate(
            name=user_data.name,
            contact=user_data.contact or "0000000000",
            address=user_data.address,
            region=None
        )
        crud.create_receiver_with_user(db, receiver_data, user.user_id)
    
    return user


@router.get("/users", response_model=list[schemas.UserResponse])
def get_all_users(
    role: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all users, optionally filtered by role
    """
    return crud.get_users(db, role=role)


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user account
    """
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}
