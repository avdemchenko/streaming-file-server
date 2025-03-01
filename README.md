# Streaming File Server

A robust Flask-based file server optimized for efficient handling of large files through chunked transfers. This solution provides a complete stack for file operations with full progress monitoring capabilities.

## Features

- **Chunked File Operations**
  - Upload large files in small manageable chunks
  - Stream file downloads with progress tracking
  - Resume interrupted uploads from where they left off
  - Visual progress bars for monitoring transfers

- **Multiple Client Options**
  - Python client with tqdm progress bars
  - Bash/curl scripts with terminal progress visualization
  - RESTful API for integration with any platform

- **RESTful API**
  - Comprehensive Swagger documentation
  - Proper status codes and consistent responses
  - Follows REST best practices

- **Security & Performance**
  - File type validation before assembly
  - Rate limiting to prevent abuse
  - CORS configuration for controlled access
  - Efficient memory usage for large files

## Requirements

- Python 3.9+
- Flask and dependencies (see requirements.txt)
- For progress visualization:
  - Python client: tqdm
  - Bash client: curl, numfmt

## Installation

### Local Development

1. Clone the repository:
   ```
   git clone <repository-url>
   cd streaming-file-server
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   **Note for macOS users**: If you encounter an error about `libmagic`, you can install it using Homebrew:
   ```
   brew install libmagic
   ```
   
   The application includes a fallback mechanism that will use Python's built-in `mimetypes` module when `libmagic` isn't available.

4. Run the application:
   ```
   python run_server.py
   ```

### Docker Deployment

1. Build and run using Docker Compose:
   ```
   docker-compose up -d
   ```

The application will be available at http://localhost:8080.

## Client Tools

The server comes with multiple client tools to demonstrate chunked uploads and downloads with progress visualization:

### Python Clients

1. **test_chunked_upload.py** - Uploads files in chunks with tqdm progress bar:
   ```
   python test_chunked_upload.py <file_path>
   ```

2. **download_file.py** - Downloads files with tqdm progress bar:
   ```
   python download_file.py <file_id> [output_path]
   ```

### Bash/Curl Clients

1. **curl_chunked_upload.sh** - Uploads files in chunks with terminal progress bar:
   ```
   chmod +x curl_chunked_upload.sh
   ./curl_chunked_upload.sh <file_path> [chunk_size_kb]
   ```

2. **curl_download.sh** - Downloads files with terminal progress bar:
   ```
   chmod +x curl_download.sh
   ./curl_download.sh <file_id> [output_filename]
   ```

## API Documentation

Once the server is running, you can access the Swagger documentation at:

```
http://localhost:8080/api/docs
```

### API Endpoints

- `POST /api/files/upload` - Upload a file (regular upload)
- `POST /api/files/upload/chunked` - Upload a file chunk (chunked upload)
- `GET /api/files/upload/chunked` - Check if a chunk exists
- `GET /api/files` - List all uploaded files
- `GET /api/files/{file_id}` - Download a file
- `DELETE /api/files/{file_id}` - Delete a file

## Chunked Upload Process

The chunked upload process works as follows:

1. **Client-side file splitting**: The file is divided into chunks of a configurable size
2. **Sequenced upload**: Each chunk is uploaded with metadata including position, total size, and a unique identifier
3. **Chunk validation**: The server validates each chunk as it arrives
4. **File assembly**: Once all chunks are received, the server assembles the complete file
5. **Type validation**: The assembled file is validated for allowed file types
6. **Cleanup**: Temporary chunks are removed after successful assembly

### Example: Multi-Gigabyte File Upload

When uploading large files:

1. Choose an appropriate chunk size (default: 256KB)
2. The server stores chunks in a temporary directory
3. Progress bars show both per-chunk and overall file progress
4. If the connection drops, you can resume from the last successfully uploaded chunk

## Security Considerations

- File types are validated after assembly using magic numbers/MIME types
- Rate limiting prevents abuse through configurable thresholds
- CORS settings control which domains can access the API
- Temporary files are cleaned up automatically

## Configuration

Edit `config.py` to adjust:

- Maximum file size
- Allowed file extensions
- Upload directory
- Chunk size
- Rate limiting settings

## Testing

Run the test suite with:

```
pytest
```

Or test specific functionality:

```
pytest tests/test_files.py
