"""
Configuration package for SkinPredict API
"""

import os
from .config import Config, DevelopmentConfig, ProductionConfig, TestingConfig

__all__ = ['Config', 'DevelopmentConfig', 'ProductionConfig', 'TestingConfig', 'get_config', 'validate_config']


def get_config(config_name=None):
    """
    Get configuration class based on environment.
    
    Args:
        config_name: Optional config name override
        
    Returns:
        Configuration class instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
        'default': DevelopmentConfig
    }
    
    return configs.get(config_name, configs['default'])


def validate_config(config):
    """
    Validate configuration settings.
    
    Args:
        config: Configuration object to validate
        
    Returns:
        bool: True if valid, raises exception if invalid
    """
    required_attrs = ['SECRET_KEY']
    
    for attr in required_attrs:
        if not hasattr(config, attr) or not getattr(config, attr):
            raise ValueError(f"Missing required configuration: {attr}")
    
    return True
