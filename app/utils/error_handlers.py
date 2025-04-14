"""
Error handlers for the application.
"""
from flask import jsonify, current_app
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    
    @app.errorhandler(400)
    def bad_request(e):
        logger.warning(f"Bad request: {str(e)}")
        return jsonify({
            "error": "bad_request", 
            "message": str(e)
        }), 400

    @app.errorhandler(401)
    def unauthorized(e):
        logger.warning(f"Unauthorized access: {str(e)}")
        return jsonify({
            "error": "unauthorized",
            "message": "Authentication required or invalid credentials"
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        logger.warning(f"Forbidden access: {str(e)}")
        return jsonify({
            "error": "forbidden",
            "message": "You don't have permission to access this resource"
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        logger.info(f"Resource not found: {str(e)}")
        return jsonify({
            "error": "not_found",
            "message": "The requested resource was not found"
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        logger.warning(f"Method not allowed: {str(e)}")
        return jsonify({
            "error": "method_not_allowed",
            "message": "The method is not allowed for the requested URL"
        }), 405

    @app.errorhandler(429)
    def too_many_requests(e):
        logger.warning(f"Rate limit exceeded: {str(e)}")
        return jsonify({
            "error": "rate_limit",
            "message": "Too many requests. Please try again later."
        }), 429

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Internal server error: {str(e)}")
        return jsonify({
            "error": "server_error",
            "message": "An internal server error occurred"
        }), 500


def register_jwt_handlers(jwt):
    """Register JWT-specific error handlers."""
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.info(f"Expired token used with payload: {jwt_payload}")
        return jsonify({
            "error": "token_expired",
            "message": "The access token has expired. Please refresh your token."
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.warning(f"Invalid token used: {error}")
        return jsonify({
            "error": "invalid_token",
            "message": "The token is invalid or malformed."
        }), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        logger.warning(f"Missing token: {error}")
        return jsonify({
            "error": "missing_token",
            "message": "Authorization token is required."
        }), 401
        
    @jwt.token_verification_failed_loader
    def verification_failed_callback():
        logger.warning("Token verification failed")
        return jsonify({
            "error": "token_verification_failed",
            "message": "Token verification failed."
        }), 401
        
    @jwt.needs_fresh_token_loader
    def needs_fresh_token_callback(jwt_header, jwt_payload):
        logger.info(f"Non-fresh token used when fresh is required: {jwt_payload}")
        return jsonify({
            "error": "fresh_token_required",
            "message": "Fresh login required for this action."
        }), 401
        
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        logger.info(f"Revoked token used: {jwt_payload}")
        return jsonify({
            "error": "token_revoked",
            "message": "This token has been revoked."
        }), 401