"""
Pytest Configuration and Fixtures
"""
import pytest
import sys
from pathlib import Path

# Add api to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    from api.app import create_app
    
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'DEBUG': False
    })
    
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI runner."""
    return app.test_cli_runner()
