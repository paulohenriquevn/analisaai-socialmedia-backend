"""
Analytics module for Analisa.ai Social Media.
"""
from app.api.analytics.routes import bp
from app.api.analytics.routes.sentiment import bp as sentiment_bp
from app.api.analytics.routes.posting_time import bp as posting_time_bp
from app.api.analytics.routes.engagement import bp as engagement_bp
from app.api.analytics.routes.reach import bp as reach_bp
from app.api.analytics.routes.growth import bp as growth_bp
from app.api.analytics.routes.score import bp as score_bp

# Verificar se o módulo de visualização está disponível
try:
    from app.api.analytics.routes.visualization import bp as visualization_bp
    has_visualization = True
except ImportError:
    has_visualization = False

if has_visualization:
    __all__ = ['bp', 'sentiment_bp', 'posting_time_bp', 'engagement_bp', 'reach_bp', 'growth_bp', 'score_bp', 'visualization_bp']
else:
    __all__ = ['bp', 'sentiment_bp', 'posting_time_bp', 'engagement_bp', 'reach_bp', 'growth_bp', 'score_bp']