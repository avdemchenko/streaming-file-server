import requests
import sys
import os
from tqdm import tqdm

def download_file(file_id, output_path=None):
    """Download a file from the streaming file server by its ID."""
    base_url = "http://localhost:8080/api/files"
    
    # Construct the download URL
    download_url = f"{base_url}/{file_id}"
    
    print(f"Downloading file with ID: {file_id}")
    
    # Send the HEAD request first to get the file size
    head_response = requests.head(download_url)
    
    # Check if the request was successful
    if head_response.status_code == 200:
        # Get the file size if possible
        file_size = int(head_response.headers.get('Content-Length', 0))
        
        # Get the filename from the Content-Disposition header if available
        content_disposition = head_response.headers.get('Content-Disposition', '')
        filename = None
        
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"\'')
        
        # If we couldn't get the filename from the header, use the file_id
        if not filename:
            filename = f"downloaded_{file_id}"
            
        # If output_path is specified, use that instead
        output_file = output_path if output_path else filename
        
        # Now send the GET request to download the file with streaming enabled
        response = requests.get(download_url, stream=True)
        
        # Get the chunk size (8KB)
        chunk_size = 8192
        
        # Create a progress bar
        progress_desc = f"Downloading {os.path.basename(output_file)}"
        
        with open(output_file, 'wb') as f:
            # Use tqdm to display download progress
            with tqdm(total=file_size, unit='B', unit_scale=True, desc=progress_desc) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        print(f"File downloaded successfully: {output_file}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        print(f"File size: {os.path.getsize(output_file)} bytes")
        return True
    else:
        print(f"Failed to download file: {head_response.status_code}")
        print(head_response.text)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_file.py <file_id> [output_path]")
        sys.exit(1)
    
    file_id = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    download_file(file_id, output_path)
