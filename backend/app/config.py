"""
Configuration module for application settings.
Loads environment variables and provides application-wide configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Smart Expiry and Donation Management System"
    DEBUG: bool = True
    
    # Database Configuration (PostgreSQL or MySQL)
    DATABASE_URL: Optional[str] = None  # Full database URL (preferred for PostgreSQL)
    
    # MySQL Configuration (fallback if not using DATABASE_URL)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: Optional[str] = None
    MYSQL_DATABASE: str = "expiry_donation_db"
    
    # MongoDB Configuration
    MONGODB_URI: str = "mongodb://localhost:27017/"
    MONGODB_DATABASE: str = "expiry_donation_nosql"
    
    # Business Logic
    EXPIRY_CHECK_DAYS: int = 30
    ALERT_CHECK_INTERVAL_HOURS: int = 24
    # Admin credentials for simple protected actions (local/dev use)
    ADMIN_USER: str = "admin"
    ADMIN_PASSWORD: str = "password"
    
    @property
    def database_url(self) -> str:
        """Get database URL - supports both PostgreSQL and MySQL."""
        if self.DATABASE_URL:
            # If using PostgreSQL, ensure we use psycopg3 dialect
            url = self.DATABASE_URL
            if url.startswith('postgresql://'):
                url = url.replace('postgresql://', 'postgresql+psycopg://', 1)
            elif url.startswith('postgres://'):
                url = url.replace('postgres://', 'postgresql+psycopg://', 1)
            
            # For Supabase pooler, ensure we're using the correct connection mode
            if 'supabase' in url and '?' not in url:
                url += '?sslmode=require'
            elif 'supabase' in url and 'sslmode' not in url:
                url += '&sslmode=require'
                
            return url
        # Fallback to MySQL if DATABASE_URL not provided
        if not self.MYSQL_PASSWORD:
            raise ValueError("Either DATABASE_URL or MYSQL_PASSWORD must be provided")
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )
    
    # Keep old property for backwards compatibility
    @property
    def mysql_url(self) -> str:
        """Construct MySQL database URL."""
        return self.database_url
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


# Global settings instance
settings = Settings()
