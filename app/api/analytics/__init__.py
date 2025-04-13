"""
Analytics module for Analisa.ai Social Media.
"""
from app.api.analytics.routes import bp
from app.api.analytics.routes.sentiment import bp as sentiment_bp
from app.api.analytics.routes.posting_time import bp as posting_time_bp

__all__ = ['bp', 'sentiment_bp', 'posting_time_bp']