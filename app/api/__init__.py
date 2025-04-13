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
    from app.api.influencers import bp as influencers_bp
    from app.api.analytics import bp as analytics_bp
    from app.api.analytics import sentiment_bp
    from app.api.analytics import posting_time_bp
    from app.api.search import bp as search_bp
    
    # Register blueprints with proper URL prefixes
    api.register_blueprint(auth_bp, url_prefix='/auth')
    api.register_blueprint(users_bp, url_prefix='/users')
    api.register_blueprint(influencers_bp, url_prefix='/influencers')
    api.register_blueprint(analytics_bp, url_prefix='/analytics')
    api.register_blueprint(sentiment_bp, url_prefix='/analytics/sentiment')
    api.register_blueprint(posting_time_bp, url_prefix='/analytics/posting-time')
    api.register_blueprint(search_bp, url_prefix='/search')
    
    # Register main API blueprint
    app.register_blueprint(api)
    
    # Register root route
    @app.route('/')
    def index():
        from flask import jsonify
        return jsonify({"message": "Welcome to Analisa.ai Social Media API"})