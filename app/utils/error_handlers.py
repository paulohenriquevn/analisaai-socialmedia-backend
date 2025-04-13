"""
Error handlers for the application.
"""
from flask import jsonify

def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "message": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500


def register_jwt_handlers(jwt):
    """Register JWT-specific error handlers."""
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Token inválido"}), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({"error": "Authorization required"}), 401