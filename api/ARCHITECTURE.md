# SkinPredict API - Optimized Architecture

## Overview
This refactored version of the SkinPredict API follows enterprise-level best practices with a clean, modular architecture that replaces the original monolithic `server.py` file.

## Architecture

### 📁 Directory Structure
```
api/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py            # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── skin_analysis_model.py  # TensorFlow skin analysis
│   │   └── fairface_model.py       # PyTorch demographic prediction
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_service.py     # Core analysis orchestration
│   │   ├── chat_service.py         # Chatbot functionality
│   │   ├── email_service.py        # Email notifications
│   │   └── product_service.py      # Product recommendations
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── image_processing.py     # OpenCV utilities
│   │   ├── groq_client.py          # GROQ API client
│   │   ├── web_scraper.py          # Product scraping
│   │   └── product_database.py     # Product data management
│   └── routes/
│       ├── __init__.py             # Blueprint registration
│       ├── analysis_routes.py      # /api/analyze endpoints
│       ├── chat_routes.py          # /api/chat endpoints
│       ├── product_routes.py       # /api/product-* endpoints
│       └── email_routes.py         # /api/send-* endpoints
├── server_optimized.py             # New main server file
└── requirements.txt
```

## 🔄 Migration from Original Server

### Before (Monolithic)
- Single `server.py` file (~1000+ lines)
- Mixed responsibilities
- Hard to maintain and test
- Tight coupling between components

### After (Modular)
- **Configuration Management**: Environment-specific settings
- **Service Layer**: Business logic separation
- **Model Wrappers**: Clean AI model interfaces
- **Route Blueprints**: RESTful API organization
- **Utility Modules**: Reusable components

## 🚀 Key Improvements

### 1. **Application Factory Pattern**
```python
# app/__init__.py
def create_app(config_name=None):
    app = Flask(__name__)
    # Load configuration
    # Initialize services
    # Register routes
    return app
```

### 2. **Dependency Injection**
Services are initialized once and shared across the application:
- `SkinAnalysisModel` - TensorFlow model wrapper
- `FairFaceModel` - PyTorch model wrapper
- `AnalysisService` - Core business logic
- `ChatService` - Chatbot with context
- `EmailService` - Email notifications
- `ProductService` - Recommendations & stores

### 3. **Clean Separation of Concerns**
- **Models**: AI model wrappers with preprocessing
- **Services**: Business logic and external API integration
- **Routes**: HTTP endpoint handlers
- **Utils**: Shared utilities and clients

### 4. **Configuration Management**
Environment-specific configurations:
- `DevelopmentConfig`
- `ProductionConfig`
- `TestingConfig`

### 5. **Error Handling & Logging**
- Comprehensive error handling throughout
- Structured logging with different levels
- Graceful degradation for external services

## 📊 API Endpoints

### Analysis
- `POST /api/analyze` - Skin analysis with image upload
- `GET /api/analyze/status` - Analysis service health

### Chat
- `POST /api/chat` - Chat with skin analysis context
- `GET /api/chat/status` - Chat service health

### Products
- `GET /api/product-recommendations` - Get product suggestions
- `GET /api/find-dermatologists` - Find nearby dermatologists
- `GET /api/nearby-stores` - Find skincare stores
- `GET /api/nearby-products` - Products with store locations

### Email
- `POST /api/send-analysis-results` - Email analysis results
- `POST /api/send-recommendations` - Email product recommendations
- `POST /api/send-custom-email` - Send custom emails
- `POST /api/test-email` - Test email configuration

### System
- `GET /health` - Service health check
- `GET /api/info` - API information

## 🔧 Running the Optimized Server

### Start the Application
```bash
python server_optimized.py
```

### Environment Variables
```bash
# Required
GROQ_API_KEY=your_groq_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_key

# Optional (with defaults)
FLASK_ENV=development
HOST=0.0.0.0
PORT=5000
DEBUG=True

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
```

## 🧪 Testing

### Unit Tests
Each service can be tested independently:
```python
# Example: Testing AnalysisService
from app.services.analysis_service import AnalysisService

def test_analysis_service():
    service = AnalysisService(models, utils)
    result = service.analyze_skin(image_data)
    assert result['skin_type'] is not None
```

### Integration Tests
Test complete workflows:
```python
# Example: Testing full analysis pipeline
def test_full_analysis():
    response = client.post('/api/analyze', 
                          files={'image': image_file})
    assert response.status_code == 200
    assert 'skin_type' in response.json
```

## 📈 Performance Benefits

1. **Faster Startup**: Services initialized once at startup
2. **Better Memory Usage**: Shared model instances
3. **Improved Scalability**: Modular components
4. **Easier Debugging**: Clear error boundaries
5. **Better Caching**: Service-level caching opportunities

## 🔐 Security Improvements

1. **Input Validation**: Proper request validation
2. **Error Sanitization**: No sensitive data in error responses
3. **Configuration Security**: Environment variable usage
4. **CORS Configuration**: Proper cross-origin handling

## 🔍 Monitoring & Debugging

1. **Structured Logging**: Consistent log format
2. **Health Checks**: Service status endpoints
3. **Error Tracking**: Detailed error logging
4. **Performance Metrics**: Service timing information

## 🚀 Deployment Ready

The optimized architecture is production-ready with:
- Environment-specific configurations
- Proper error handling
- Scalable service architecture
- Clean separation of concerns
- Comprehensive logging
- Health monitoring endpoints

This refactored version transforms the original monolithic code into a maintainable, scalable, and professional API that follows industry best practices.
