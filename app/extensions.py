"""
Flask extensions initialization.
These are initialized separately from create_app() to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from flask_caching import Cache

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
oauth = OAuth()
cache = Cache()

def init_extensions(app):
    """Initialize all extensions with the app."""
    # Swagger/OpenAPI (Flasgger)
    from flasgger import Swagger
    Swagger(app)
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register JWT error handlers
    from app.utils.error_handlers import register_jwt_handlers
    register_jwt_handlers(jwt)
    
    # Configure cache
    cache_config = {
        'CACHE_TYPE': 'SimpleCache',  # Use simple in-memory cache
        'CACHE_DEFAULT_TIMEOUT': 300,  # Default timeout is 5 minutes
        'CACHE_KEY_PREFIX': 'analisaai_',  # Add a prefix to avoid collisions
    }
    app.config.from_mapping(cache_config)
    cache.init_app(app)

    # Initialize Redis for JWT blacklist
    from redis import Redis
    app.redis = Redis.from_url(app.config.get('REDIS_URL', 'redis://localhost:6379/0'))

    # Initialize Flask-Limiter for rate limiting
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri=app.config.get('REDIS_URL', 'redis://localhost:6379/0'),
        default_limits=["100 per minute"]
    )
    app.limiter = limiter

    # Configure OAuth
    oauth.init_app(app)
    
    # Configure OAuth clients
    from app.services.oauth_service import config_oauth
    config_oauth(app)