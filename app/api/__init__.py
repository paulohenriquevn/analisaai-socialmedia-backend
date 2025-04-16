"""
API initialization and blueprint registration.
"""
from flask import Blueprint

# Create main API blueprint
api = Blueprint('api', __name__, url_prefix='/api')

def init_app(app):
    """Register all API blueprints."""
    # Import blueprints
    from app.api.auth import bp as auth_bp
    from app.api.users import bp as users_bp
    from app.api.social_page import bp as social_page_bp
    from app.api.analytics import bp as analytics_bp
    from app.api.analytics import sentiment_bp
    from app.api.analytics import posting_time_bp
    from app.api.analytics import engagement_bp
    from app.api.analytics import reach_bp
    from app.api.analytics import growth_bp
    from app.api.analytics import score_bp
    from app.api.search import bp as search_bp
    from app.api.dashboard import bp as dashboard_bp
    from app.api.social_media import bp as social_media_bp
    from app.api.analytics import visualization_bp
    
    
    # Register blueprints with proper URL prefixes
    api.register_blueprint(auth_bp, url_prefix='/auth')
    api.register_blueprint(users_bp, url_prefix='/users')
    api.register_blueprint(analytics_bp, url_prefix='/analytics')
    api.register_blueprint(sentiment_bp, url_prefix='/analytics/sentiment')
    api.register_blueprint(posting_time_bp, url_prefix='/analytics/posting-time')
    api.register_blueprint(engagement_bp, url_prefix='/analytics/engagement')
    api.register_blueprint(reach_bp, url_prefix='/analytics/reach')
    api.register_blueprint(growth_bp, url_prefix='/analytics/growth')
    api.register_blueprint(score_bp, url_prefix='/analytics/score')
    api.register_blueprint(visualization_bp, url_prefix='/analytics/visualization')
    api.register_blueprint(search_bp, url_prefix='/search')
    api.register_blueprint(social_page_bp, url_prefix='/social-page')
    api.register_blueprint(social_media_bp, url_prefix='/social-media')
    api.register_blueprint(dashboard_bp)  # Dashboard endpoints
    
    # Register main API blueprint
    app.register_blueprint(api)
    
    # Register root route
    @app.route('/')
    def index():
        from flask import jsonify
        return jsonify({"message": "Welcome to Analisa.ai Social Media API"})