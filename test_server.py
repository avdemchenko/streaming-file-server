#!/usr/bin/env python3
import requests
import sys

def check_server():
    """Simple script to check if the server is running and accessible."""
    print("Checking server connection...")
    
    urls = [
        "http://localhost:8080/",
        "http://localhost:8080/api/",
        "http://localhost:8080/api/docs/",
        "http://localhost:8080/api/files"
    ]
    
    for url in urls:
        try:
            print(f"\nTrying to connect to: {url}")
            response = requests.get(url, timeout=5)
            print(f"  Status code: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")
            if len(response.content) < 500:
                print(f"  Content: {response.text}")
            else:
                print(f"  Content length: {len(response.content)} bytes")
        except requests.ConnectionError as e:
            print(f"  Error: Could not connect to {url}")
            print(f"  {str(e)}")
        except Exception as e:
            print(f"  Error: {str(e)}")

if __name__ == "__main__":
    check_server()
