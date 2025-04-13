"""
Application entry point for Analisa.ai Social Media.
"""
import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create app instance using environment configuration
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Get configuration from environment or use defaults
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # Start the Flask application
    app.run(host=host, port=port, debug=debug)