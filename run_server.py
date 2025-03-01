#!/usr/bin/env python3
import os
from pathlib import Path
from app import create_app
from config import Config

if __name__ == '__main__':
    # Make sure the upload directory exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Create a temp directory for chunked uploads if it doesn't exist
    temp_dir = Config.UPLOAD_FOLDER / "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Upload directory: {Config.UPLOAD_FOLDER}")
    print(f"Allowed extensions: {Config.ALLOWED_EXTENSIONS}")
    
    # Create and run the app
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
