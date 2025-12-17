"""
Simple admin router for login/verification endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..config import settings

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(req: LoginRequest):
    """Validate admin credentials. Returns success boolean for client-side gating."""
    if req.username == settings.ADMIN_USER and req.password == settings.ADMIN_PASSWORD:
        return {"access": True}
    raise HTTPException(status_code=401, detail="Invalid credentials")
