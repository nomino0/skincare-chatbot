"""
Application factory for SkinPredict API.
Creates and configures the Flask application with all components.
"""

import logging
from flask import Flask
from flask_cors import CORS
from pathlib import Path

from .config import get_config, validate_config
from .models import SkinAnalysisModel, FairFaceModel
from .services import AnalysisService, ChatService, EmailService, ProductService
from .utils import ImageProcessor, GroqClient, WebScraper, ProductDatabase
from .routes import register_blueprints


def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name: Configuration environment name.
        
    Returns:
        Configured Flask application.
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Validate configuration
    try:
        validate_config(config)
    except ValueError as e:
        app.logger.error(f"Configuration validation failed: {e}")
        # Continue with warning in development, but this should be fixed for production
    
    # Initialize configuration
    config.init_app(app)
    
    # Set up logging
    _setup_logging(app)

    # Setup credentials from env vars if needed (for cloud deployment)
    try:
        from .utils.setup_credentials import setup_firebase_credentials
        setup_firebase_credentials()
    except ImportError:
        pass
    
    # Initialize CORS
    CORS(app, origins=config.CORS_ORIGINS)
    
    # Initialize services
    services = _initialize_services(app, config)
    
    # Store services in app context for access in routes
    app.services = services
    
    # Initialize database
    _initialize_database(app)

    # Auto-create admin if configured
    _create_initial_admin(app)
    
    # Initialize agent tools with services
    _initialize_agent(app, services)
    
    # Register API routes
    register_blueprints(app)
    
    # Error handlers
    _register_error_handlers(app)
    
    app.logger.info("SkinPredict API application created successfully")
    return app


def _setup_logging(app):
    """Set up application logging."""
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    logging.basicConfig(
        level=log_level,
        format=app.config.get('LOG_FORMAT', '%(asctime)s %(levelname)s %(name)s %(message)s')
    )
    
    if not app.debug:
        # Set up file logging for production
        import os
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/skinpredict.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(app.config.get('LOG_FORMAT'))
        )
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(log_level)


def _initialize_services(app, config):
    """
    Initialize all application services.
    
    Args:
        app: Flask application instance.
        config: Configuration object.
        
    Returns:
        Dictionary of initialized services.
    """
    services = {}
    
    # Initialize utilities
    app.logger.info("Initializing utilities...")
    
    image_processor = ImageProcessor()
    services['image_processor'] = image_processor
    
    groq_client = None
    if config.GROQ_API_KEY:
        groq_client = GroqClient(
            api_key=config.GROQ_API_KEY,
            timeout=config.EXTERNAL_API_TIMEOUT
        )
    services['groq_client'] = groq_client
    
    web_scraper = WebScraper(request_timeout=config.EXTERNAL_API_TIMEOUT)
    services['web_scraper'] = web_scraper
    
    product_database = ProductDatabase()
    services['product_database'] = product_database
    
    # Initialize AI models
    app.logger.info("Initializing AI models...")
    
    skin_model = SkinAnalysisModel(
        model_paths=config.MODEL_PATHS,
        confidence_threshold=config.MODEL_CONFIDENCE_THRESHOLD
    )
    services['skin_model'] = skin_model
    
    # FairFace model is DISABLED to save memory and startup time
    fairface_model = None
    # if config.FAIRFACE_MODEL_PATH:
    #     from pathlib import Path as PathLib
    #     fairface_path = PathLib(config.FAIRFACE_MODEL_PATH)
    #     fairface_model = FairFaceModel(model_path=fairface_path)
    # else:
    #     app.logger.info("FairFace model not configured - demographics will use defaults")
    
    services['fairface_model'] = fairface_model
    
    # Initialize business services
    app.logger.info("Initializing business services...")
    
    analysis_service = AnalysisService(
        skin_model=skin_model,
        fairface_model=fairface_model,
        image_processor=image_processor,
        groq_client=groq_client
    )
    services['analysis_service'] = analysis_service
    
    product_service = ProductService(
        web_scraper=web_scraper,
        product_database=product_database,
        google_maps_api_key=config.GOOGLE_MAPS_API_KEY,
        max_products=config.MAX_PRODUCT_RECOMMENDATIONS,
        request_timeout=config.EXTERNAL_API_TIMEOUT
    )
    services['product_service'] = product_service
    
    if groq_client:
        chat_service = ChatService(
            groq_client=groq_client,
            product_service=product_service
        )
        services['chat_service'] = chat_service
    
    email_service = EmailService(
        smtp_host=config.EMAIL_HOST,
        smtp_port=config.EMAIL_PORT,
        username=config.EMAIL_USERNAME,
        password=config.EMAIL_PASSWORD,
        use_tls=config.EMAIL_USE_TLS,
        product_service=product_service
    )
    services['email_service'] = email_service
    
    app.logger.info("All services initialized successfully")
    return services


def _initialize_database(app):
    """Initialize database tables."""
    try:
        from .database import init_db
        init_db()
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")


def _initialize_agent(app, services):
    """Initialize LangGraph agent with service dependencies."""
    try:
        from .agent import set_services
        set_services(
            analysis_service=services.get('analysis_service'),
            product_service=services.get('product_service')
        )
        app.logger.info("Agent tools initialized successfully")
    except Exception as e:
        app.logger.error(f"Agent initialization failed: {e}")


def _create_initial_admin(app):
    """Create initial admin user if configured in environment."""
    if not app.config.get('ADMIN_EMAIL') or not app.config.get('ADMIN_PASSWORD'):
        return

    try:
        from .database import get_db
        from .models.sql_models import User
        
        # Use a new context for this operation
        with app.app_context():
            # Get session from generator
            db = next(get_db())
            try:
                email = app.config['ADMIN_EMAIL']
                admin = db.query(User).filter_by(email=email).first()
                if not admin:
                    app.logger.info(f"Creating initial admin user: {email}")
                    new_admin = User(
                        email=email,
                        role='admin',
                        firebase_uid=f"admin_{email}" # Placeholder UID for non-firebase auth
                    )
                    db.add(new_admin)
                    db.commit()
                    app.logger.info("Initial admin created successfully")
            except Exception as e:
                 app.logger.error(f"Failed to create initial admin: {e}")
            finally:
                db.close()
    except Exception as e:
        app.logger.error(f"Error in admin initialization: {e}")


def _register_error_handlers(app):
    """Register global error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'message': str(error)}, 400
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {'error': 'Method not allowed', 'message': str(error)}, 405
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return {'error': 'Internal server error', 'message': 'An unexpected error occurred'}, 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f'Unhandled exception: {e}', exc_info=True)
        return {'error': 'Internal server error', 'message': 'An unexpected error occurred'}, 500
