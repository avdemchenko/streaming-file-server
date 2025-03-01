from flask import Flask
from flask_restx import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app(config_class=Config):
    """Factory function to create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # Initialize rate limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config['RATELIMIT_DEFAULT']],
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )
    
    # Setup API with Swagger documentation
    api = Api(
        app, 
        version='1.0', 
        title='Streaming File Server API',
        description='A RESTful API for efficient file operations with chunked uploads and downloads',
        doc='/api/docs',
        validate=True,
        prefix='/api'  # Add prefix to all routes
    )
    
    # Import and register blueprints/namespaces
    from api.files import api as files_ns
    api.add_namespace(files_ns, path='/files')  # Explicitly set the path
    
    # CORS Configuration
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
    
    # Add error handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return {'message': 'File too large'}, 413
    
    @app.errorhandler(404)
    def not_found(error):
        return {'message': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return {'message': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
