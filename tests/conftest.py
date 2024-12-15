import pytest

from app import create_app
from app.core.file_service import FileService


@pytest.fixture
def app():
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def upload_folder(app):
    folder = app.config['UPLOAD_FOLDER']
    folder.mkdir(parents=True, exist_ok=True)
    yield folder
    # Cleanup after tests
    for file in folder.glob('*'):
        file.unlink()
    folder.rmdir()


@pytest.fixture
def file_service(upload_folder):
    return FileService(upload_folder)
