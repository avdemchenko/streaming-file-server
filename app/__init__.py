from pathlib import Path

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_swagger_ui import get_swaggerui_blueprint

from app.config import config

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def create_app(config_name='default'):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    CORS(app)
    limiter.init_app(app)

    # Ensure UPLOAD_FOLDER is a Path object and create it if it doesn't exist
    app.config['UPLOAD_FOLDER'] = Path(app.config['UPLOAD_FOLDER'])
    app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)

    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)

    # Configure Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Streaming File Server API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
