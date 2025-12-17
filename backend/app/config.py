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
    
    # MySQL Configuration
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str
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
    def mysql_url(self) -> str:
        """Construct MySQL database URL."""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


# Global settings instance
settings = Settings()
