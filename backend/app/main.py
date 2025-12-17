"""
FastAPI Main Application
Smart Expiry and Donation Management System
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import logging

from .config import settings
from .database import init_db, close_db_connections, get_db
from . import crud, schemas
from .routers import donors, categories, items, receivers, donations, alerts, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting application...")
    try:
        init_db()
        logger.info("✓ Database initialized successfully")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    close_db_connections()
    logger.info("✓ Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="A DBMS-centric full-stack application for expiry tracking and donation management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Include Routers
# ============================================================================

app.include_router(donors.router)
app.include_router(categories.router)
app.include_router(items.router)
app.include_router(receivers.router)
app.include_router(donations.router)
app.include_router(alerts.router)
app.include_router(admin.router)


# ============================================================================
# Root & Health Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "DBMS-centric full-stack application",
        "docs": "/docs",
        "health": "/health",
        "database": {
            "mysql": settings.MYSQL_DATABASE,
            "mongodb": settings.MONGO_DATABASE
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected"
    }


@app.get("/api/stats", response_model=schemas.DashboardStats, tags=["Statistics"])
def get_statistics(db: Session = Depends(get_db)):
    """
    Get dashboard statistics.
    Aggregates data from multiple tables for analytics.
    """
    return crud.get_dashboard_stats(db)


# ============================================================================
# Error Handlers
# ============================================================================

from fastapi import Request, status
from fastapi.responses import JSONResponse


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# Startup Message
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
