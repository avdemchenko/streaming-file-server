import os
import uuid
import logging
import mimetypes
from pathlib import Path
from flask import request, send_file, current_app, Response
from flask_restx import Namespace, Resource, fields, reqparse
from werkzeug.utils import secure_filename

# Initialize the namespace
api = Namespace('files', description='File operations')

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize mimetypes
mimetypes.init()
# Add additional mappings
mimetypes.add_type('application/json', '.ipynb')

# Try importing python-magic, but fall back to mimetypes if not available
try:
    import magic
    has_magic = True
except ImportError:
    logger.warning("python-magic not available, falling back to mimetypes")
    has_magic = False

# Models for Swagger documentation
file_info = api.model('FileInfo', {
    'id': fields.String(description='Unique file identifier'),
    'filename': fields.String(description='Original filename'),
    'size': fields.Integer(description='File size in bytes'),
    'content_type': fields.String(description='File MIME type'),
    'upload_date': fields.DateTime(description='Upload timestamp')
})

# Upload parsers
upload_parser = reqparse.RequestParser()
upload_parser.add_argument('file', location='files', type='file', required=True, help='File to upload')

chunk_parser = reqparse.RequestParser()
chunk_parser.add_argument('flowChunkNumber', type=int, required=True, help='Current chunk number')
chunk_parser.add_argument('flowTotalChunks', type=int, required=True, help='Total number of chunks')
chunk_parser.add_argument('flowChunkSize', type=int, required=True, help='General chunk size')
chunk_parser.add_argument('flowTotalSize', type=int, required=True, help='Total file size')
chunk_parser.add_argument('flowIdentifier', required=True, help='Unique identifier for the file')
chunk_parser.add_argument('flowFilename', required=True, help='Original file name')
chunk_parser.add_argument('file', location='files', type='file', required=True, help='Chunk data')

# Helper functions
def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_mime_type(file_path):
    """Get MIME type using magic if available, otherwise fall back to mimetypes."""
    if has_magic:
        mime = magic.Magic(mime=True)
        return mime.from_file(str(file_path))
    else:
        # Fallback to mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'

def validate_file_type(file_path):
    """Validate file type using either python-magic or mimetypes."""
    file_type = get_mime_type(file_path)
    logger.info(f"File MIME type detected: {file_type}")
    
    # Define allowed MIME types based on your security requirements
    allowed_mime_types = [
        'text/plain', 'application/pdf', 'image/png', 'image/jpeg',
        'image/gif', 'video/mp4', 'application/zip', 'application/json',
        'application/octet-stream', 'application/x-ipynb+json'
    ]
    
    if file_type in allowed_mime_types:
        logger.info(f"File type validated: {file_type}")
        return True
    else:
        logger.warning(f"Unsupported file type: {file_type}")
        return False

def get_file_list():
    """Get list of uploaded files."""
    files = []
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    for file_path in upload_folder.glob('*'):
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                'id': file_path.name,
                'filename': file_path.name,
                'size': stat.st_size,
                'content_type': get_mime_type(str(file_path)),
                'upload_date': stat.st_mtime
            })
    
    return files


@api.route('/upload')
class FileUpload(Resource):
    """Endpoint for regular (non-chunked) file uploads."""
    
    @api.expect(upload_parser)
    @api.response(201, 'File uploaded successfully')
    @api.response(400, 'Invalid file')
    @api.response(415, 'Unsupported file type')
    def post(self):
        """Upload a file (for files up to 5GB)."""
        try:
            # Get the file directly from request.files instead of using the parser
            if 'file' not in request.files:
                api.abort(400, "No file part in the request")
                
            file = request.files['file']
            
            if file.filename == '':
                api.abort(400, "No file selected")
            
            if not allowed_file(file.filename):
                api.abort(400, "File type not allowed")
            
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            file_path = current_app.config['UPLOAD_FOLDER'] / file_id
            
            # Save the file
            file.save(str(file_path))
            
            # Validate file type
            if not validate_file_type(file_path):
                os.remove(str(file_path))
                api.abort(415, "Unsupported file type")
            
            return {
                'id': file_id,
                'filename': filename,
                'size': os.path.getsize(str(file_path)),
                'content_type': get_mime_type(str(file_path))
            }, 201
        except Exception as e:
            logger.error(f"Error during file upload: {str(e)}")
            api.abort(500, f"Error processing file: {str(e)}")


@api.route('/upload/chunked')
class ChunkedUpload(Resource):
    """Endpoint for chunked file uploads."""
    
    @api.expect(chunk_parser)
    @api.response(201, 'Chunk uploaded successfully')
    @api.response(200, 'Chunk already exists')
    @api.response(400, 'Invalid chunk data')
    def post(self):
        """Upload a file chunk."""
        try:
            # Get parameters from request directly instead of using the parser
            if 'file' not in request.files:
                api.abort(400, "No file part in the request")
                
            # Extract data from request
            chunk_number = int(request.form['flowChunkNumber'])
            total_chunks = int(request.form['flowTotalChunks'])
            chunk_size = int(request.form['flowChunkSize'])
            total_size = int(request.form['flowTotalSize'])
            identifier = request.form['flowIdentifier']
            filename = secure_filename(request.form['flowFilename'])
            file = request.files['file']
            
            if not allowed_file(filename):
                api.abort(400, "File type not allowed")
            
            # Create a directory for temporary chunk storage
            temp_dir = current_app.config['UPLOAD_FOLDER'] / "temp" / identifier
            os.makedirs(temp_dir, exist_ok=True)
            
            # Define chunk path
            chunk_path = temp_dir / f"chunk.{chunk_number}"
            
            # Check if chunk already exists
            if os.path.exists(chunk_path) and os.path.getsize(chunk_path) == chunk_size:
                return {'message': 'Chunk already exists'}, 200
            
            # Save the chunk
            file.save(chunk_path)
            logger.info(f"Chunk {chunk_number}/{total_chunks} uploaded for {filename}")
            
            # Check if all chunks have been uploaded
            uploaded_chunks = list(temp_dir.glob("chunk.*"))
            if len(uploaded_chunks) == total_chunks:
                # All chunks received, combine them
                file_id = str(uuid.uuid4())
                output_path = current_app.config['UPLOAD_FOLDER'] / file_id
                
                with open(output_path, 'wb') as output_file:
                    for i in range(1, total_chunks + 1):
                        chunk_file = temp_dir / f"chunk.{i}"
                        with open(chunk_file, 'rb') as input_file:
                            output_file.write(input_file.read())
                
                # Validate file type
                if not validate_file_type(output_path):
                    os.remove(output_path)
                    api.abort(415, "Unsupported file type detected")
                
                # Clean up chunks
                for chunk_file in uploaded_chunks:
                    os.remove(chunk_file)
                os.rmdir(temp_dir)
                
                logger.info(f"File assembled: {filename} (ID: {file_id})")
                
                return {
                    'id': file_id,
                    'filename': filename,
                    'size': os.path.getsize(output_path),
                    'content_type': get_mime_type(str(output_path))
                }, 201
                
            return {'message': f'Chunk {chunk_number} uploaded successfully'}, 201
            
        except KeyError as e:
            logger.error(f"Missing required parameter: {str(e)}")
            api.abort(400, f"Missing required parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Chunk upload error: {str(e)}")
            api.abort(500, f"Chunk upload failed: {str(e)}")
    
    @api.expect(chunk_parser)
    @api.response(200, 'Chunk exists')
    @api.response(204, 'Chunk does not exist')
    def get(self):
        """
        Check if a chunk already exists.
        Used for resumable uploads to avoid re-uploading existing chunks.
        """
        args = chunk_parser.parse_args()
        
        chunk_number = args['flowChunkNumber']
        identifier = args['flowIdentifier']
        
        # Check if the chunk exists
        temp_dir = current_app.config['UPLOAD_FOLDER'] / "temp" / identifier
        chunk_path = temp_dir / f"chunk.{chunk_number}"
        
        if os.path.exists(chunk_path):
            return {'message': 'Chunk exists'}, 200
        else:
            return '', 204  # No content


@api.route('/files')
class FileList(Resource):
    """Endpoint to list all uploaded files."""
    
    @api.marshal_list_with(file_info)
    @api.response(200, 'Success')
    def get(self):
        """Get a list of all uploaded files."""
        return get_file_list()


@api.route('/files/<string:file_id>')
@api.param('file_id', 'The file identifier')
class FileResource(Resource):
    """Endpoint for file operations on a specific file."""
    
    @api.response(200, 'Success')
    @api.response(404, 'File not found')
    def get(self, file_id):
        """Download a file by ID."""
        file_path = current_app.config['UPLOAD_FOLDER'] / file_id
        
        if not os.path.exists(file_path):
            api.abort(404, "File not found")
        
        # Get original filename if available (stored in metadata)
        original_filename = file_id  # Default to ID if original name not available
        
        # Stream the file in chunks
        def generate():
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(current_app.config['CHUNK_SIZE'])
                    if not chunk:
                        break
                    yield chunk
        
        mime = get_mime_type(str(file_path))
        
        # Log the download
        logger.info(f"File download started: {file_id}")
        
        # Stream response
        return Response(
            generate(),
            mimetype=mime,
            headers={
                'Content-Disposition': f'attachment; filename="{original_filename}"',
                'Content-Type': mime
            }
        )
    
    @api.response(204, 'File deleted')
    @api.response(404, 'File not found')
    def delete(self, file_id):
        """Delete a file by ID."""
        file_path = current_app.config['UPLOAD_FOLDER'] / file_id
        
        if not os.path.exists(file_path):
            api.abort(404, "File not found")
        
        try:
            os.remove(file_path)
            logger.info(f"File deleted: {file_id}")
            return '', 204
        except Exception as e:
            logger.error(f"File deletion error: {str(e)}")
            api.abort(500, f"File deletion failed: {str(e)}")
