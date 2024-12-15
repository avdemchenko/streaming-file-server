import os
from pathlib import Path


class Config:
    # Base configuration
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPLOAD_FOLDER = Path(os.getenv('UPLOAD_FOLDER', BASE_DIR / 'uploads'))
    MAX_CONTENT_LENGTH = None  # No file size limit
    CHUNK_SIZE = 8192  # 8KB chunks for streaming

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip'}

    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    UPLOAD_FOLDER = Path(__file__).parent.parent / 'tests' / 'uploads'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
