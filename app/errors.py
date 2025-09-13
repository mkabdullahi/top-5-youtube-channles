from flask import jsonify
from werkzeug.exceptions import HTTPException
import traceback

class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class RateLimitError(APIError):
    """Raised when API rate limit is exceeded"""
    def __init__(self, message="Rate limit exceeded", payload=None):
        super().__init__(message, status_code=429, payload=payload)

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    def __init__(self, message="Authentication failed", payload=None):
        super().__init__(message, status_code=401, payload=payload)

class PlatformError(APIError):
    """Raised when a platform-specific error occurs"""
    def __init__(self, platform, message, payload=None):
        super().__init__(
            message=f"Error with {platform}: {message}",
            status_code=502,
            payload=payload
        )

def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        response = jsonify({
            'status': 'error',
            'message': error.description,
        })
        response.status_code = error.code
        return response

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        # Log the full error with traceback
        app.logger.error(f"Unexpected error: {str(error)}")
        app.logger.error(traceback.format_exc())
        
        response = jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred'
        })
        response.status_code = 500
        return response

    @app.errorhandler(429)
    def handle_rate_limit(error):
        return jsonify({
            'status': 'error',
            'message': 'Rate limit exceeded. Please try again later.'
        }), 429