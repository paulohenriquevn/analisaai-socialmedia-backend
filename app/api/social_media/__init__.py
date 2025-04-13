"""Social media module."""
from flask import Blueprint

bp = Blueprint('social_media', __name__)

# Import routes to register them
from app.api.social_media.routes import connect
