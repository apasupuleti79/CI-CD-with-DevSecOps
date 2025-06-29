from flask import Flask, jsonify, request
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['VERSION'] = os.environ.get('APP_VERSION', '1.0.0')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': app.config['VERSION']
    }), 200

@app.route('/api/info')
def app_info():
    """Application information endpoint"""
    return jsonify({
        'name': 'DevSecOps Demo Application',
        'version': app.config['VERSION'],
        'description': 'A sample application demonstrating DevSecOps practices',
        'features': [
            'Security scanning integration',
            'Automated CI/CD pipeline',
            'Container security',
            'Monitoring and alerting'
        ]
    }), 200

@app.route('/api/secure-data')
def secure_data():
    """Endpoint demonstrating secure data handling"""
    # Input validation
    user_id = request.args.get('user_id')
    if not user_id or not user_id.isdigit():
        return jsonify({'error': 'Invalid user ID'}), 400
    
    # Simulated secure data response
    return jsonify({
        'user_id': int(user_id),
        'data': 'This is secure data',
        'access_time': datetime.utcnow().isoformat()
    }), 200

@app.route('/')
def index():
    """Main page"""
    return jsonify({
        'message': 'Welcome to DevSecOps Demo Application',
        'version': app.config['VERSION'],
        'endpoints': {
            'health': '/health',
            'info': '/api/info',
            'secure_data': '/api/secure-data?user_id=123'
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting DevSecOps Demo Application v{app.config['VERSION']}")
    app.run(host='0.0.0.0', port=port, debug=debug)
