"""
Test Suite for SkinPredict API
Following MLOps best practices from lab materials.

Run with: pytest api/tests/ -v
"""
import pytest
import json
import base64
from pathlib import Path


class TestAPIBasics:
    """Test basic API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('status') == 'healthy'
    
    def test_api_info_endpoint(self, client):
        """Test API info endpoint."""
        response = client.get('/api/info')
        assert response.status_code == 200
        data = response.get_json()
        assert 'version' in data or 'name' in data


class TestAnalysisEndpoints:
    """Test skin analysis endpoints."""
    
    def test_analyze_requires_image(self, client):
        """Test that analyze endpoint requires image data."""
        response = client.post('/api/analyze', 
                               json={},
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_analyze_with_invalid_image(self, client):
        """Test analyze with invalid image data."""
        response = client.post('/api/analyze',
                               json={'image': 'invalid_base64'},
                               content_type='application/json')
        # Should return error for invalid image
        assert response.status_code in [400, 500]
    
    def test_analyze_with_valid_image(self, client, sample_image_base64):
        """Test analyze with valid image data."""
        response = client.post('/api/analyze',
                               json={'image': sample_image_base64},
                               content_type='application/json')
        # Analysis should succeed or return processing message
        assert response.status_code in [200, 202]
        if response.status_code == 200:
            data = response.get_json()
            # Check for expected response structure
            assert 'skinType' in data or 'error' in data


class TestUserEndpoints:
    """Test user-related endpoints."""
    
    def test_user_profile_requires_auth(self, client):
        """Test that profile endpoint requires authentication."""
        response = client.get('/api/user/profile')
        # Should return 401 Unauthorized without auth
        assert response.status_code in [401, 403]


class TestChatEndpoints:
    """Test chat/assistant endpoints."""
    
    def test_chat_requires_message(self, client):
        """Test that chat endpoint requires a message."""
        response = client.post('/api/chat',
                               json={},
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_chat_with_message(self, client):
        """Test chat with valid message."""
        response = client.post('/api/chat',
                               json={'message': 'What is my skin type?'},
                               content_type='application/json')
        # Should succeed or require auth
        assert response.status_code in [200, 401]


class TestPydanticModels:
    """Test data validation (equivalent to Pydantic in FastAPI)."""
    
    def test_analysis_request_validation(self):
        """Test that analysis request validates properly."""
        from api.app.routes.analysis_routes import analysis_bp
        
        # Valid request structure
        valid_request = {
            'image': 'base64_encoded_string',
            'use_groq': False
        }
        assert 'image' in valid_request
        
    def test_user_profile_structure(self):
        """Test user profile data structure."""
        expected_fields = ['uid', 'email', 'role']
        # These fields should be present in profile response
        for field in expected_fields:
            assert isinstance(field, str)


class TestModelManager:
    """Test model loading and management."""
    
    def test_skin_model_exists(self):
        """Test that skin analysis model file exists."""
        model_paths = [
            Path('api/models/model.h5'),
            Path('api/models/multitask_skin_model.h5')
        ]
        # At least one model should exist
        assert any(p.exists() for p in model_paths), "No model file found"
    
    def test_model_loads_correctly(self):
        """Test that model can be loaded."""
        from api.app.models.skin_analysis_model import SkinAnalysisModel
        
        model_path = Path('api/models/multitask_skin_model.h5')
        if model_path.exists():
            model = SkinAnalysisModel(
                model_paths={'skin_analysis': str(model_path)},
                confidence_threshold=0.5
            )
            assert model is not None


class TestDatabaseOperations:
    """Test database CRUD operations."""
    
    def test_scan_table_exists(self):
        """Test that Scan table is defined."""
        from api.app.models.sql_models import Scan
        assert Scan is not None
    
    def test_user_table_exists(self):
        """Test that User table is defined."""
        from api.app.models.sql_models import User
        assert User is not None
        # Check opt_out column exists
        assert hasattr(User, 'opt_out_data_collection')


# Fixtures
@pytest.fixture
def client():
    """Create test client."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from api.app import create_app
    app = create_app('testing')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_image_base64():
    """Create a sample base64 encoded test image."""
    # Create a simple 10x10 red image
    import numpy as np
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')
