#!/usr/bin/env python3
import os
import sys
import traceback
from pathlib import Path
from config import Config

try:
    print("Starting server setup...")
    
    # Make sure the upload directory exists
    upload_dir = Config.UPLOAD_FOLDER
    print(f"Creating upload directory: {upload_dir}")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create a temp directory for chunked uploads if it doesn't exist
    temp_dir = upload_dir / "temp"
    print(f"Creating temp directory: {temp_dir}")
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Upload directory: {upload_dir}")
    print(f"Allowed extensions: {Config.ALLOWED_EXTENSIONS}")
    
    # Check for the presence of mimetypes or magic library
    import mimetypes
    print("Mimetypes module loaded successfully")
    
    try:
        import magic
        print("Python-magic loaded successfully")
    except ImportError:
        print("Python-magic not available, will use mimetypes fallback")
    
    print("Importing Flask app...")
    from app import create_app
    
    print("Creating Flask app...")
    app = create_app()
    
    # Print out the registered routes
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    
    print("\nStarting Flask server on http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    print("\nDetailed traceback:")
    traceback.print_exc()
    sys.exit(1)
