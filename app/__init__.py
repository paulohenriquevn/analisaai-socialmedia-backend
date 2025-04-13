from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
import datetime

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/analisaai')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=30)
    
    # Social Media OAuth configurations
    app.config['INSTAGRAM_CLIENT_ID'] = os.getenv('INSTAGRAM_CLIENT_ID', '')
    app.config['INSTAGRAM_CLIENT_SECRET'] = os.getenv('INSTAGRAM_CLIENT_SECRET', '')
    app.config['INSTAGRAM_REDIRECT_URI'] = os.getenv('INSTAGRAM_REDIRECT_URI', 'http://localhost:5000/api/auth/instagram/callback')
    
    app.config['FACEBOOK_CLIENT_ID'] = os.getenv('FACEBOOK_CLIENT_ID', '')
    app.config['FACEBOOK_CLIENT_SECRET'] = os.getenv('FACEBOOK_CLIENT_SECRET', '')
    app.config['FACEBOOK_REDIRECT_URI'] = os.getenv('FACEBOOK_REDIRECT_URI', 'http://localhost:5000/api/auth/facebook/callback')
    
    app.config['TIKTOK_CLIENT_ID'] = os.getenv('TIKTOK_CLIENT_ID', '')
    app.config['TIKTOK_CLIENT_SECRET'] = os.getenv('TIKTOK_CLIENT_SECRET', '')
    app.config['TIKTOK_REDIRECT_URI'] = os.getenv('TIKTOK_REDIRECT_URI', 'http://localhost:5000/api/auth/tiktok/callback')
    
    # Override config if provided
    if config:
        app.config.update(config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Set up logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/analisaai.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Analisa.ai Social Media startup')
    
    # Register CLI commands
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database tables and default data."""
        from app.models import Role, Category
        
        # Create all tables
        db.create_all()
        app.logger.info("Created database tables")
        
        # Initialize roles
        from app.services.security_service import init_roles
        init_roles(db)
        app.logger.info("Initialized user roles")
        
        # Create categories if they don't exist
        categories = [
            {'name': 'Fashion', 'description': 'Fashion, clothing, and style'},
            {'name': 'Beauty', 'description': 'Beauty products and makeup'},
            {'name': 'Travel', 'description': 'Travel and tourism'},
            {'name': 'Fitness', 'description': 'Fitness and exercise'},
            {'name': 'Food', 'description': 'Food and cooking'},
            {'name': 'Technology', 'description': 'Technology and gadgets'},
            {'name': 'Gaming', 'description': 'Video games and gaming'},
            {'name': 'Entertainment', 'description': 'Entertainment and celebrity news'},
            {'name': 'Lifestyle', 'description': 'Lifestyle and daily life'},
            {'name': 'Business', 'description': 'Business and entrepreneurship'}
        ]
        
        for category_data in categories:
            if not Category.query.filter_by(name=category_data['name']).first():
                category = Category(**category_data)
                db.session.add(category)
        
        db.session.commit()
        app.logger.info("Initialized categories")
        app.logger.info("Database initialization complete")
    
    with app.app_context():
        # Import models so they are registered with SQLAlchemy
        from . import models
        
        # Set up OAuth
        from .services.oauth_service import config_oauth
        config_oauth(app)
        
        # Import and register views
        from .views import main, register_error_handlers
        
        # Register blueprints
        app.register_blueprint(main)
        
        # Register error handlers
        register_error_handlers(app)
    
    return app

# Create the application instance
app = create_app() 