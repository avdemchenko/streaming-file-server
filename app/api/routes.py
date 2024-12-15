from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context

from app.core.file_service import FileService
from app.core.security import allowed_file
from app.utils.helpers import error_response

api_bp = Blueprint('api', __name__, url_prefix='/api')


def get_file_service():
    """Get or create FileService instance"""
    if not hasattr(current_app, 'file_service'):
        current_app.file_service = FileService(
            upload_folder=current_app.config['UPLOAD_FOLDER'],
            chunk_size=current_app.config['CHUNK_SIZE']
        )
    return current_app.file_service


@api_bp.route('/files', methods=['POST'])
def upload_file():
    """Upload a file in chunks with progress"""
    if 'file' not in request.files:
        return error_response('No file part', 400)

    file = request.files['file']
    if file.filename == '':
        return error_response('No selected file', 400)

    if not allowed_file(file.filename):
        return error_response('File type not allowed', 400)

    offset = int(request.form.get('offset', 0))
    total_size = request.content_length

    try:
        result = get_file_service().save_file_chunk(
            file,
            file.filename,
            offset=offset,
            total_size=total_size
        )
        return jsonify(result), 200
    except Exception as e:
        return error_response(str(e), 500)


@api_bp.route('/files/<filename>', methods=['GET'])
def download_file(filename):
    """Download a file in chunks with progress"""
    result = get_file_service().get_file_stream(filename)
    if not result:
        return error_response('File not found', 404)

    stream, file_size = result

    response = Response(
        stream_with_context(stream()),
        mimetype='application/octet-stream',
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Length': file_size
        }
    )

    return response


@api_bp.route('/files', methods=['GET'])
def list_files():
    """List all files"""
    try:
        files = get_file_service().list_files()
        return jsonify(files), 200
    except Exception as e:
        return error_response(str(e), 500)


@api_bp.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a file"""
    if get_file_service().delete_file(filename):
        return '', 204
    return error_response('File not found', 404)
