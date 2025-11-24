"""
Routes package for SkinPredict API.
Contains API endpoint blueprints organized by functionality.
"""

from flask import Blueprint
from .analysis_routes import analysis_bp
from .chat_routes import chat_bp
from .product_routes import product_bp
from .email_routes import email_bp


def register_blueprints(app):
    """
    Register all API blueprints with the Flask application.
    
    Args:
        app: Flask application instance.
    """
    # Register API blueprints
    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(product_bp, url_prefix='/api')
    app.register_blueprint(email_bp, url_prefix='/api')
    
    # Add health check route
    @app.route('/health')
    def health_check():
        """Simple health check endpoint."""
        return {'status': 'healthy', 'message': 'SkinPredict API is running'}
    
    # Add API info route
    @app.route('/api/info')
    def api_info():
        """API information endpoint."""
        return {
            'name': 'SkinPredict API',
            'version': '2.0.0',
            'description': 'AI-powered skin analysis and product recommendation API',
            'endpoints': {
                'analysis': '/api/analyze',
                'chat': '/api/chat',
                'products': '/api/product-recommendations',
                'stores': '/api/nearby-stores',
                'email': '/api/send-analysis-results'
            }
        }
    
    app.logger.info("All API blueprints registered successfully")
