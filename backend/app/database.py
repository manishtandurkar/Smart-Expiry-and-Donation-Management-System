"""
Database connection management for MySQL and MongoDB.
Provides session management and connection pooling.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pymongo import MongoClient
from pymongo.database import Database
from typing import Generator
from .config import settings

# ============================================================================
# MySQL Database Setup (SQLAlchemy)
# ============================================================================

# Create database engine with connection pooling
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# MongoDB Database Setup (PyMongo)
# ============================================================================

# MongoDB client with connection pooling (optional)
mongo_client = None
mongo_db = None

try:
    mongo_client = MongoClient(
        settings.MONGODB_URI,
        maxPoolSize=50,
        minPoolSize=10,
        serverSelectionTimeoutMS=2000
    )
    # Test connection
    mongo_client.admin.command('ping')
    # Get database instance
    mongo_db: Database = mongo_client[settings.MONGODB_DATABASE]
    print("✓ MongoDB connected successfully")
except Exception as e:
    print(f"⚠ MongoDB connection failed (optional): {str(e)}")
    print("  App will run with MySQL only - NoSQL logging disabled")


def get_mongo_db() -> Database:
    """
    Get MongoDB database instance.
    
    Usage in FastAPI:
        @app.get("/alerts/mongo")
        def read_mongo_alerts(db: Database = Depends(get_mongo_db)):
            return list(db.alerts.find())
    
    Returns:
        Database: MongoDB database instance or None if not available
    """
    return mongo_db


# ============================================================================
# Database Initialization
# ============================================================================

def init_db():
    """
    Initialize database tables.
    Should be called once during application startup.
    """
    # Import all models to register them with Base
    from . import models
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ MySQL tables created successfully")
    
    # Create MongoDB indexes if available
    if mongo_db is not None:
        try:
            mongo_db.alerts.create_index("item_id")
            mongo_db.alerts.create_index("alert_date")
            mongo_db.alerts.create_index([("alert_date", -1)])  # Descending for recent first
            print("✓ MongoDB indexes created successfully")
        except Exception as e:
            print(f"⚠ MongoDB index creation failed: {str(e)}")


def close_db_connections():
    """
    Close all database connections.
    Should be called during application shutdown.
    """
    engine.dispose()
    if mongo_client is not None:
        mongo_client.close()
    print("✓ Database connections closed")
