

"""
Configuration settings for Telemetry Sleuth application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'telemetrysleuth')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    # TCP Listener configuration
    TCP_HOST = os.getenv('TCP_HOST', '0.0.0.0')
    TCP_PORT = int(os.getenv('TCP_PORT', '9000'))
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Application settings
    MAX_RECORDS_PER_PAGE = int(os.getenv('MAX_RECORDS_PER_PAGE', '100'))
    
    @property
    def DATABASE_URL(self):
        """Construct database URL from components."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DB_NAME = os.getenv('TEST_DB_NAME', 'telemetrysleuth_test')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}