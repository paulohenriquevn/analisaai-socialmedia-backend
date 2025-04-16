"""
Dashboard metrics API endpoints.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import (
    SocialPage, SocialPageMetric, SocialPageScore, SocialPagePost, OptimizationTip
)
from sqlalchemy import desc, func

bp = Blueprint('dashboard', __name__)

# Endpoint 1: Métricas Principais
@bp.route('/api/metrics/<int:social_page>', methods=['GET'])
@jwt_required()
def get_main_metrics(social_page):
    """Retorna métricas principais com valores atuais e variação percentual mensal."""
    # Busca o último registro de métricas
    latest_metric = SocialPageMetric.query.filter_by(social_page_id=social_page).order_by(desc(SocialPageMetric.date)).first()
    month_ago_metric = SocialPageMetric.query.filter_by(social_page_id=social_page).order_by(desc(SocialPageMetric.date)).offset(30).first()

    def percent_change(current, previous):
        if previous and previous != 0:
            return round(100 * (current - previous) / previous, 1)
        return 0.0

    if not latest_metric:
        return jsonify([])

    metrics = [
        {
            "id": 1,
            "title": "Seguidores",
            "current_value": latest_metric.followers or 0,
            "monthly_change_percent": percent_change(latest_metric.followers or 0, month_ago_metric.followers if month_ago_metric else 0),
            "category": "followers"
        },
        {
            "id": 2,
            "title": "Engajamento",
            "current_value": latest_metric.engagement or 0,
            "monthly_change_percent": percent_change(latest_metric.engagement or 0, month_ago_metric.engagement if month_ago_metric else 0),
            "category": "engagement"
        },
        {
            "id": 3,
            "title": "Impressões",
            "current_value": latest_metric.views or 0,
            "monthly_change_percent": percent_change(latest_metric.views or 0, month_ago_metric.views if month_ago_metric else 0),
            "category": "impressions"
        },
        {
            "id": 4,
            "title": "Alcance",
            "current_value": getattr(latest_metric, 'reach', 0) or 0,
            "monthly_change_percent": percent_change(getattr(latest_metric, 'reach', 0) or 0, getattr(month_ago_metric, 'reach', 0) if month_ago_metric else 0),
            "category": "reach"
        },
    ]
    return jsonify(metrics)

# Endpoint 2: Scores de Desempenho
@bp.route('/api/social-scores/<int:social_page>', methods=['GET'])
@jwt_required()
def get_social_scores(social_page):
    """Retorna o score social geral e os subscores de desempenho."""
    score = SocialPageScore.query.filter_by(social_page_id=social_page).order_by(desc(SocialPageScore.date)).first()
    if not score:
        return jsonify({"overall_social_score": 0, "breakdown": []})
    breakdown = [
        {"metric": "Crescimento de Seguidores", "score": int(score.growth_score or 0)},
        {"metric": "Engajamento", "score": int(score.engagement_score or 0)},
        {"metric": "Alcance", "score": int(score.reach_score or 0)}
    ]
    return jsonify({
        "overall_social_score": int(score.overall_score or 0),
        "breakdown": breakdown
    })

# Endpoint 3: Posts Destacados
@bp.route('/api/top-posts/<int:social_page>', methods=['GET'])
@jwt_required()
def get_top_posts(social_page):
    """Retorna os posts com maior engajamento."""
    posts = SocialPagePost.query.filter_by(social_page_id=social_page).order_by(desc(SocialPagePost.engagement)).limit(3).all()
    result = [
        {
            "id": post.id,
            "image_url": post.media_url,
            "caption": post.content,
            "likes": post.likes_count or 0,
            "comments": post.comments_count or 0,
            "impressions": post.impressions_count or 0
        }
        for post in posts
    ]
    return jsonify(result)

# Endpoint 4: Dicas de Otimização
@bp.route('/api/optimization-tips/<int:social_page>', methods=['GET'])
@jwt_required()
def get_optimization_tips(social_page):
    """Retorna recomendações para melhorar o desempenho nas redes sociais."""
    tips = OptimizationTip.query.filter_by(social_page_id=social_page).all()
    result = [
        {
            "id": tip.id,
            "title": tip.title,
            "description": tip.description,
            "implementation_status": tip.implementation_status
        }
        for tip in tips
    ]
    return jsonify(result)

# PATCH para atualizar status da dica
@bp.route('/api/optimization-tips/<int:tip_id>', methods=['PATCH'])
@jwt_required()
def update_optimization_tip(tip_id):
    data = request.get_json()
    tip = OptimizationTip.query.get_or_404(tip_id)
    if 'implementation_status' in data:
        tip.implementation_status = data['implementation_status']
        db.session.commit()
    return jsonify({
        "id": tip.id,
        "implementation_status": tip.implementation_status
    })
