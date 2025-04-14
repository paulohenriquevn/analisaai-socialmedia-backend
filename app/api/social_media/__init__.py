"""Social media module."""
from flask import Blueprint

bp = Blueprint('social_media', __name__)

# Import routes to register them
from app.api.social_media.routes import connect
from app.api.social_media.routes import update_influencer
from app.api.social_media.routes.apify_test import apify_test_bp

# Register sub-blueprints
bp.register_blueprint(apify_test_bp, url_prefix='/apify')
