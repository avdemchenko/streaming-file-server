import io


def test_upload_file(client):
    data = {
        'file': (io.BytesIO(b'test content'), 'test.txt'),
        'offset': '0'
    }
    response = client.post('/api/files', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert 'filename' in response.json
    assert response.json['filename'] == 'test.txt'


def test_upload_invalid_file(client):
    data = {
        'file': (io.BytesIO(b'test content'), 'test.invalid'),
        'offset': '0'
    }
    response = client.post('/api/files', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert 'error' in response.json


def test_download_file(client, upload_folder):
    # First upload a file
    test_content = b'test content'
    with open(upload_folder / 'test.txt', 'wb') as f:
        f.write(test_content)

    response = client.get('/api/files/test.txt')
    assert response.status_code == 200
    assert response.data == test_content


def test_list_files(client, upload_folder):
    # Create some test files
    test_files = ['test1.txt', 'test2.txt']
    for filename in test_files:
        with open(upload_folder / filename, 'wb') as f:
            f.write(b'test content')

    response = client.get('/api/files')
    assert response.status_code == 200
    files = response.json
    assert len(files) == 2
    assert all(f['filename'] in test_files for f in files)


def test_delete_file(client, upload_folder):
    # Create a test file
    test_file = upload_folder / 'test.txt'
    test_file.write_bytes(b'test content')

    response = client.delete('/api/files/test.txt')
    assert response.status_code == 204
    assert not test_file.exists()
