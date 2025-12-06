"""
Configuration settings for SkinPredict API.
Contains environment-specific configurations for development, testing, and production.
"""

import os
from pathlib import Path


class Config:
    """Base configuration class with common settings."""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'skinpredict_admin_secret')
    
    # API settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = False
    
    # CORS settings
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # External API settings
    
    # Email settings (optional)
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    EMAIL_USE_TLS = True
    
    # Logging settings
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @staticmethod
    def init_app(app):
        """Initialize app-specific configuration."""
        pass


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    ENV = 'development'
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    EXTERNAL_API_TIMEOUT = int(os.environ.get('EXTERNAL_API_TIMEOUT', 10))
    # Default model paths for development
    MODEL_PATHS = {
        'skin_analysis': os.path.join(Path(__file__).parent.parent.parent, 'models', 'multitask_skin_model.h5')
    }
    MODEL_CONFIDENCE_THRESHOLD = float(os.environ.get('MODEL_CONFIDENCE_THRESHOLD', 0.5))
    FAIRFACE_MODEL_PATH = os.environ.get('FAIRFACE_MODEL_PATH')
    MAX_PRODUCT_RECOMMENDATIONS = int(os.environ.get('MAX_PRODUCT_RECOMMENDATIONS', 5))
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    # Use eager mode for local development (no Redis required)
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    ENV = 'production'
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    EXTERNAL_API_TIMEOUT = int(os.environ.get('EXTERNAL_API_TIMEOUT', 10))
    MODEL_PATHS = os.environ.get('MODEL_PATHS')
    MODEL_CONFIDENCE_THRESHOLD = float(os.environ.get('MODEL_CONFIDENCE_THRESHOLD', 0.5))
    FAIRFACE_MODEL_PATH = os.environ.get('FAIRFACE_MODEL_PATH')
    MAX_PRODUCT_RECOMMENDATIONS = int(os.environ.get('MAX_PRODUCT_RECOMMENDATIONS', 5))
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    ENV = 'testing'