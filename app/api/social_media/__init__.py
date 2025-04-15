"""Social media module."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('social_media', __name__)

# Import routes
from app.api.social_media.routes.apify_test import apify_test_bp
from app.api.social_media.routes.tasks import bp as tasks_bp

# Register sub-blueprints
bp.register_blueprint(apify_test_bp, url_prefix='/apify')
# Register tasks blueprint without additional prefix to avoid double nesting
bp.register_blueprint(tasks_bp)

# Import all route modules to register their routes
from app.api.social_media.routes import connect
from app.api.social_media.routes import sync
from app.api.social_media.routes import update_influencer

# Add a test endpoint directly on the main blueprint
@bp.route('/test', methods=['GET'])
@jwt_required()
def test_endpoint():
    """Test endpoint to verify blueprint registration."""
    return jsonify({
        "status": "success",
        "message": "Social media blueprint is working correctly"
    })
