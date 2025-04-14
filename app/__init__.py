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
    """
    Create and configure a Flask application instance.
    
    Args:
        config_name: Configuration environment (development, testing, production)
        
    Returns:
        Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Determine config based on environment variable or default to development
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
        # Import models to ensure they're registered with SQLAlchemy
        from app import models
        
        # Register error handlers
        from app.utils.error_handlers import register_error_handlers
        register_error_handlers(app)
        
        # Register API blueprints
        from app.api import init_app
        init_app(app)
        
        # Initialize NLP resources for sentiment analysis
        try:
            import nltk
            # Download required NLTK resources for Portuguese
            resources = ['punkt', 'stopwords', 'rslp']
            for resource in resources:
                try:
                    nltk.download(resource, quiet=True)
                except Exception as e:
                    app.logger.warning(f"Could not download NLTK resource {resource}: {str(e)}")
        except ImportError:
            app.logger.warning("NLTK not installed. Sentiment analysis will use fallback methods.")
        
        # Start task queue worker threads
        try:
            from app.services import task_queue_service
            task_queue_service.start_workers()
            app.logger.info(f"Started {task_queue_service.NUM_WORKERS} task queue worker threads")
            
            # Register a function to stop workers when the app context tears down
            @app.teardown_appcontext
            def stop_task_workers(exception=None):
                task_queue_service.stop_workers()
                app.logger.info("Stopped task queue worker threads")
        except Exception as e:
            app.logger.error(f"Error starting task queue workers: {str(e)}")
    
    return app