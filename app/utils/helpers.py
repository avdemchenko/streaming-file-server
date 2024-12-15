from flask import jsonify


def error_response(message: str, status_code: int):
    """Create a standardized error response"""
    response = jsonify({
        'error': message
    })
    response.status_code = status_code
    return response
