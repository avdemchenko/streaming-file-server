import os
import tempfile
import pytest
from app import create_app
from config import Config
from pathlib import Path
import io
import uuid


class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    # Use a temporary directory for uploads
    UPLOAD_FOLDER = Path(tempfile.mkdtemp())


@pytest.fixture
def app():
    """Create application for tests."""
    app = create_app(TestConfig)
    yield app
    # Clean up temporary files after tests
    import shutil
    shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)


@pytest.fixture
def client(app):
    """Create a test client."""
    with app.test_client() as client:
        yield client


def test_file_upload(client):
    """Test regular file upload."""
    # Create a test file
    data = {
        'file': (io.BytesIO(b'This is a test file'), 'test.txt')
    }
    
    # Send file upload request
    response = client.post('/files/upload', data=data, content_type='multipart/form-data')
    
    # Check response
    assert response.status_code == 201
    json_data = response.get_json()
    assert 'id' in json_data
    assert 'filename' in json_data
    assert 'size' in json_data
    assert json_data['size'] == 17  # Length of 'This is a test file'
    
    # Verify file exists
    file_path = TestConfig.UPLOAD_FOLDER / json_data['id']
    assert os.path.exists(file_path)
    with open(file_path, 'rb') as f:
        content = f.read()
        assert content == b'This is a test file'


def test_disallowed_file_type(client):
    """Test upload with disallowed file extension."""
    # Create a test file with disallowed extension
    data = {
        'file': (io.BytesIO(b'Executable content'), 'malicious.exe')
    }
    
    # Send file upload request
    response = client.post('/files/upload', data=data, content_type='multipart/form-data')
    
    # Should be rejected
    assert response.status_code == 400


def test_chunked_upload(client, app):
    """Test chunked file upload."""
    # Create a unique identifier for this upload
    identifier = str(uuid.uuid4())
    
    # Create temporary chunks directory
    chunks_dir = app.config['UPLOAD_FOLDER'] / "temp" / identifier
    os.makedirs(chunks_dir, exist_ok=True)
    
    # Upload 3 chunks
    chunks = [b'Chunk 1 content', b'Chunk 2 content', b'Chunk 3 content']
    total_chunks = len(chunks)
    
    for i, chunk_content in enumerate(chunks, 1):
        data = {
            'flowChunkNumber': i,
            'flowTotalChunks': total_chunks,
            'flowChunkSize': len(chunk_content),
            'flowTotalSize': sum(len(c) for c in chunks),
            'flowIdentifier': identifier,
            'flowFilename': 'test.txt',
            'file': (io.BytesIO(chunk_content), 'blob')
        }
        
        response = client.post('/files/upload/chunked', data=data, content_type='multipart/form-data')
        
        # Each chunk should be accepted
        assert response.status_code in [200, 201]
    
    # After all chunks uploaded, verify the file exists and has correct content
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    assert len(files) > 0  # At least one file should exist (ignore temp dir)
    
    # Find the final assembled file
    final_file = None
    for f in files:
        if f != 'temp':
            final_file = f
            break
    
    assert final_file is not None
    
    # Check file content
    with open(app.config['UPLOAD_FOLDER'] / final_file, 'rb') as f:
        content = f.read()
        assert content == b'Chunk 1 contentChunk 2 contentChunk 3 content'


def test_file_download(client, app):
    """Test file download."""
    # First upload a file
    test_content = b'Download test content'
    file_id = str(uuid.uuid4())
    file_path = app.config['UPLOAD_FOLDER'] / file_id
    
    with open(file_path, 'wb') as f:
        f.write(test_content)
    
    # Now try to download it
    response = client.get(f'/files/{file_id}')
    
    # Verify response
    assert response.status_code == 200
    assert response.data == test_content
    assert 'Content-Disposition' in response.headers
    assert 'attachment' in response.headers['Content-Disposition']


def test_file_list(client, app):
    """Test listing uploaded files."""
    # Create a few test files
    for i in range(3):
        file_id = str(uuid.uuid4())
        file_path = app.config['UPLOAD_FOLDER'] / file_id
        with open(file_path, 'wb') as f:
            f.write(f'Test file {i}'.encode())
    
    # Request file list
    response = client.get('/files')
    
    # Verify response
    assert response.status_code == 200
    files = response.get_json()
    assert isinstance(files, list)
    assert len(files) == 3  # Should have 3 files
    
    # Check file info structure
    for file in files:
        assert 'id' in file
        assert 'filename' in file
        assert 'size' in file
        assert 'content_type' in file


def test_file_delete(client, app):
    """Test file deletion."""
    # Create a test file
    file_id = str(uuid.uuid4())
    file_path = app.config['UPLOAD_FOLDER'] / file_id
    with open(file_path, 'wb') as f:
        f.write(b'Test file for deletion')
    
    # Delete the file
    response = client.delete(f'/files/{file_id}')
    
    # Verify response
    assert response.status_code == 204
    
    # Verify file was deleted
    assert not os.path.exists(file_path)
