import requests
import os
import sys
import uuid
import math
from tqdm import tqdm

def chunked_upload(file_path, chunk_size=1024*1024):
    """Upload a file in chunks to the streaming file server."""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    
    # Generate a unique identifier for this upload
    identifier = str(uuid.uuid4())
    
    # Calculate number of chunks
    total_chunks = math.ceil(file_size / chunk_size)
    
    print(f"Uploading {file_name} ({file_size} bytes) in {total_chunks} chunks")
    
    base_url = "http://localhost:8080/api/files/upload/chunked"
    
    # Create progress bar for the overall file upload
    with tqdm(total=file_size, unit='B', unit_scale=True, desc="Total Upload") as pbar:
        with open(file_path, 'rb') as f:
            for chunk_number in range(1, total_chunks + 1):
                # Seek to the appropriate position in the file
                f.seek((chunk_number - 1) * chunk_size)
                
                # Read the chunk
                chunk_data = f.read(chunk_size)
                actual_chunk_size = len(chunk_data)
                
                # First check if the chunk already exists
                params = {
                    'flowChunkNumber': chunk_number,
                    'flowTotalChunks': total_chunks,
                    'flowChunkSize': chunk_size,
                    'flowTotalSize': file_size,
                    'flowIdentifier': identifier,
                    'flowFilename': file_name
                }
                
                check_response = requests.get(base_url, params=params)
                
                # If the chunk exists (status code 200), skip it
                if check_response.status_code == 200:
                    print(f"Chunk {chunk_number} already exists, skipping")
                    pbar.update(actual_chunk_size)
                    continue
                
                # Otherwise, upload the chunk
                files = {'file': ('blob', chunk_data)}
                
                print(f"Uploading chunk {chunk_number}/{total_chunks} ({actual_chunk_size} bytes)")
                
                response = requests.post(
                    base_url,
                    data=params,
                    files=files
                )
                
                # Update the progress bar with the size of this chunk
                pbar.update(actual_chunk_size)
                
                if response.status_code in (200, 201):
                    print(f"Chunk {chunk_number} uploaded successfully")
                    
                    # Check if this was the last chunk and if assembly was successful
                    if chunk_number == total_chunks and 'id' in response.json():
                        print("\nAll chunks uploaded and file assembled successfully!")
                        print(response.json())
                else:
                    print(f"Chunk {chunk_number} upload failed: {response.status_code}")
                    print(response.text)
                    return

if __name__ == "__main__":
    # Use command line argument if provided, otherwise use default file
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "/Users/user/Downloads/tutorial.ipynb"
    
    # Use smaller chunks for demonstration (256KB)
    chunked_upload(file_path, chunk_size=256*1024)
