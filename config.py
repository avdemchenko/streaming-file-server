import os
from pathlib import Path

class Config:
    # Base directory for file storage
    UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
    
    # Allowed file extensions (can be modified as needed)
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'zip', 'ipynb'}
    
    # Maximum file size for regular upload (5GB)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 * 1024
    
    # Chunk size for streaming (1MB)
    CHUNK_SIZE = 1024 * 1024
    
    # Rate limiting configuration
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

    @staticmethod
    def init_app(app):
        # Create upload directory if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Create temp directory for chunked uploads
        temp_dir = Config.UPLOAD_FOLDER / "temp"
        os.makedirs(temp_dir, exist_ok=True)
