from datetime import datetime
from pathlib import Path
from typing import Dict, List

from werkzeug.utils import secure_filename


class FileService:
    def __init__(self, upload_folder: Path, chunk_size: int = 8192):
        self.upload_folder = upload_folder
        self.chunk_size = chunk_size

    def save_file_chunk(self, file_stream, filename: str, offset: int = 0) -> Dict:
        """Save a chunk of a file to disk"""
        filepath = self.upload_folder / secure_filename(filename)

        mode = 'ab' if offset > 0 else 'wb'
        with open(filepath, mode) as f:
            f.seek(offset)
            f.write(file_stream.read())

        return {
            'filename': filename,
            'size': filepath.stat().st_size,
            'offset': offset + self.chunk_size
        }

    def get_file_stream(self, filename: str):
        """Get a file stream for downloading"""
        filepath = self.upload_folder / secure_filename(filename)
        if not filepath.exists():
            return None

        def generate():
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    yield chunk

        return generate()

    def list_files(self) -> List[Dict]:
        """List all files with their metadata"""
        files = []
        for filepath in self.upload_folder.glob('*'):
            if filepath.is_file():
                stat = filepath.stat()
                files.append({
                    'filename': filepath.name,
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        return files

    def delete_file(self, filename: str) -> bool:
        """Delete a file"""
        filepath = self.upload_folder / secure_filename(filename)
        if filepath.exists():
            filepath.unlink()
            return True
        return False
