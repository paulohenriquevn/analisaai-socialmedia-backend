"""Social media module."""
from flask import Blueprint

bp = Blueprint('social_media', __name__)

# Import routes to register them
from app.api.social_media.routes.apify_test import apify_test_bp
from app.api.social_media.routes.tasks import bp as tasks_bp

# Register sub-blueprints
bp.register_blueprint(apify_test_bp, url_prefix='/apify')
# Register tasks blueprint without additional prefix to avoid double nesting
bp.register_blueprint(tasks_bp)
