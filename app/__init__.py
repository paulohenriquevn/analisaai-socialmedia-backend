"""
Application factory for Analisa.ai Social Media.
"""
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask

from app.extensions import init_extensions
from app.config import config


def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
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
    
    # Initialize extensions
    init_extensions(app)
    
    # Register API blueprints
    with app.app_context():
        # Register error handlers
        from app.utils.error_handlers import register_error_handlers
        register_error_handlers(app)
        
        # Register API blueprints
        from app.api import init_app
        init_app(app)

    return app