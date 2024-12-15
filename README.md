# Streaming File Server

A Flask-based streaming file server that supports uploading and downloading large files efficiently using chunked transfer.

## Features

- Upload files of any size using chunked uploads
- Stream downloads to handle large files efficiently
- RESTful API for file operations
- File type validation
- Rate limiting
- CORS support
- Docker support
- Swagger API documentation

## Requirements

- Python 3.9+
- Poetry for dependency management
- Docker (optional)

## Installation

### Local Development

1. Clone the repository:

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
or
```bash
brew install poetry
```
3. Install dependencies:
```bash
poetry install
```
4. Set up environment variables:
```bash
cp .env.example .env
```
5. Run the server:
```bash
poetry run flask run --port=3000
```
or
```bash
docker-compose up dev
```
