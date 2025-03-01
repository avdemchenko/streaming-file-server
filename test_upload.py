import requests
import sys
import os
from pathlib import Path
import argparse

def check_server_connection(base_url):
    """Check if the server is running and accessible."""
    try:
        docs_url = f"{base_url}/api/docs/"
        print(f"Checking server connection: {docs_url}")
        response = requests.get(docs_url)
        print(f"Server is running, status code: {response.status_code}")
        return True
    except requests.ConnectionError:
        print(f"Error: Could not connect to the server at {base_url}")
        print("Make sure the server is running with: python run_server.py")
        return False

def upload_file(file_path, port=8080):
    """Upload a file to the streaming file server."""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    base_url = f"http://localhost:{port}"
    
    # First check if server is running
    if not check_server_connection(base_url):
        return
    
    file_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)
    print(f"Uploading file: {filename} ({file_size} bytes)")
    
    url = f"{base_url}/api/files/upload"
    print(f"POST request to: {url}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            print("Sending request...")
            response = requests.post(url, files=files)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        try:
            print(f"Response content: {response.text}")
        except:
            print("Could not print response content")
        
        if response.status_code == 201:
            print("Upload successful!")
            print(response.json())
        else:
            print(f"Upload failed with status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error during upload: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload a file to the streaming server')
    parser.add_argument('--file', '-f', help='Path to the file to upload', default="/Users/user/Downloads/tutorial.ipynb")
    parser.add_argument('--port', '-p', help='Server port (default: 8080)', type=int, default=8080)
    args = parser.parse_args()
    
    upload_file(args.file, port=args.port)
