import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Generator

from tqdm import tqdm
from werkzeug.utils import secure_filename


class FileService:
    def __init__(self, upload_folder: Path, chunk_size: int = 8192):
        self.upload_folder = upload_folder
        self.chunk_size = chunk_size

    def save_file_chunk(self, file_stream, filename: str, offset: int = 0, total_size: int = None) -> Dict:
        """Save a chunk of a file to disk with progress"""
        filepath = self.upload_folder / secure_filename(filename)

        mode = 'ab' if offset > 0 else 'wb'
        with open(filepath, mode) as f:
            f.seek(offset)

            # Create progress bar if total size is known
            if total_size:
                with tqdm(total=total_size, initial=offset, unit='B', unit_scale=True,
                          desc=f"Uploading {filename}") as pbar:
                    while True:
                        chunk = file_stream.read(self.chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        pbar.update(len(chunk))
            else:
                f.write(file_stream.read())

        current_size = filepath.stat().st_size
        return {
            'filename': filename,
            'size': current_size,
            'offset': current_size,
            'total_size': total_size
        }

    def get_file_stream(self, filename: str) -> Generator:
        """Get a file stream for downloading with progress"""
        filepath = self.upload_folder / secure_filename(filename)
        if not filepath.exists():
            return None

        file_size = os.path.getsize(filepath)

        def generate():
            with open(filepath, 'rb') as f:
                with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Downloading {filename}") as pbar:
                    while True:
                        chunk = f.read(self.chunk_size)
                        if not chunk:
                            break
                        pbar.update(len(chunk))
                        yield chunk

        return generate(), file_size

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
