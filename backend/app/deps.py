"""
Dependency helpers for security checks (simple admin password header)
"""
from fastapi import Header, HTTPException, status
from .config import settings
from typing import Generator
from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    """
    Lazily import and delegate to the actual `get_db` in `database.py`.
    This avoids importing `pymongo` (optional) at module import time which
    can break application startup when `pymongo` is not installed.
    """
    from . import database

    # delegate to the database.get_db generator
    yield from database.get_db()


def get_mongo_db():
    """Lazily return the MongoDB database instance (or None)."""
    from . import database

    return database.get_mongo_db()


def verify_admin(x_admin_password: str | None = Header(None)):
    """Verify incoming request contains correct admin password header.

    Header name: `X-Admin-Password`
    """
    if not x_admin_password or x_admin_password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin credentials")
    return True
