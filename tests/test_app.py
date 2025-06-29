import pytest
import json
from src.app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'version' in data

def test_app_info(client):
    """Test the application info endpoint"""
    response = client.get('/api/info')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['name'] == 'DevSecOps Demo Application'
    assert 'version' in data
    assert 'features' in data
    assert len(data['features']) > 0

def test_secure_data_valid_user(client):
    """Test secure data endpoint with valid user ID"""
    response = client.get('/api/secure-data?user_id=123')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['user_id'] == 123
    assert 'data' in data
    assert 'access_time' in data

def test_secure_data_invalid_user(client):
    """Test secure data endpoint with invalid user ID"""
    response = client.get('/api/secure-data?user_id=invalid')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data

def test_secure_data_no_user(client):
    """Test secure data endpoint without user ID"""
    response = client.get('/api/secure-data')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data

def test_index_page(client):
    """Test the main index page"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data
    assert 'endpoints' in data

def test_not_found(client):
    """Test 404 error handling"""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert 'error' in data

def test_app_configuration():
    """Test application configuration"""
    with app.app_context():
        assert app.config['TESTING'] == True
        assert 'SECRET_KEY' in app.config
        assert 'VERSION' in app.config
