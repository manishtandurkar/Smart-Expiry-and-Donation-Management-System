"""
Dependency helpers for security checks (simple admin password header)
"""
from fastapi import Header, HTTPException, status
from .config import settings


def verify_admin(x_admin_password: str | None = Header(None)):
    """Verify incoming request contains correct admin password header.

    Header name: `X-Admin-Password`
    """
    if not x_admin_password or x_admin_password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin credentials")
    return True
