import logging
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from common.user import User
from common.social_media import SocialPage
from app.extensions import db

bp = Blueprint('social-accounts', __name__)
logger = logging.getLogger(__name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_social_accounts():
    user_id = int(get_jwt_identity())
    pages = SocialPage.query.filter_by(user_id=user_id).all()
    social_accounts = []
    for page in pages:
        social_accounts.append({
            "id": page.id,
            "platform": page.platform,
            "username": page.username,
            "profileUrl": page.profile_url,
            "profilePicture": page.profile_image,
            "followers": page.followers_count,
            "following": page.following_count,
            "postsCount": page.posts_count,
            "isConnected": True,  # Ajuste conforme lógica real
            "connectedAt": page.created_at.isoformat() if page.created_at else None,
            "token": None  # Pode buscar em SocialToken se necessário
        })
    return jsonify({
        "success": True,
        "message": "Social accounts retrieved successfully",
        "social_accounts": social_accounts
    }), 200


@bp.route('/', methods=['POST'])
@jwt_required()
def post_social_accounts():
    user_id = int(get_jwt_identity())
    data = request.json or {}
    required_fields = ["platform", "username"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    page = SocialPage(
        user_id=user_id,
        platform=data["platform"],
        username=data["username"],
        profile_url=data.get("profileUrl"),
        profile_image=data.get("profilePicture"),
        followers_count=data.get("followers", 0),
        following_count=data.get("following", 0),
        posts_count=data.get("postsCount", 0),
        created_at=data.get("connectedAt"),
    )
    db.session.add(page)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Social account created successfully",
        "social_account": {
            "id": page.id,
            "userId": page.user_id,
            "platform": page.platform,
            "username": page.username,
            "profileUrl": page.profile_url,
            "profilePicture": page.profile_image,
            "followers": page.followers_count,
            "following": page.following_count,
            "postsCount": page.posts_count,
            "isConnected": True,
            "connectedAt": page.created_at.isoformat() if page.created_at else None
        }
    }), 201


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_social_account(id):
    user_id = int(get_jwt_identity())
    page = SocialPage.query.filter_by(id=id, user_id=user_id).first()
    if not page:
        return jsonify({"error": "Social account not found"}), 404
    db.session.delete(page)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Social account deleted successfully"
    }), 200


@bp.route('/metrics/basic', methods=['GET'])
@jwt_required()
def get_social_account_basic_metrics():
    user_id = int(get_jwt_identity())
    pages = SocialPage.query.filter_by(user_id=user_id).all()
    platforms = []
    engagement_timeseries = []
    social_score = {
        "overall": 0,
        "submetrics": {"engagement": 0, "reach": 0, "growth": 0},
        "history": []
    }
    from common.social_media import SocialPageMetric, SocialPageScore
    for page in pages:
        # Última métrica
        metric = SocialPageMetric.query.filter_by(social_page_id=page.id).order_by(SocialPageMetric.date.desc()).first()
        # Score
        score = SocialPageScore.query.filter_by(social_page_id=page.id).order_by(SocialPageScore.date.desc()).first()
        platforms.append({
            "platform": page.platform,
            "followers": metric.followers if metric else 0,
            "engagement": metric.engagement if metric else 0,
            "impressions": metric.impressions if metric and hasattr(metric, 'impressions') else 0,
            "reach": metric.reach if metric and hasattr(metric, 'reach') else 0,
            "growth": 0  # Pode ser calculado a partir de métricas históricas
        })
        # Timeseries de engajamento
        metrics = SocialPageMetric.query.filter_by(social_page_id=page.id).order_by(SocialPageMetric.date.asc()).all()
        for m in metrics:
            engagement_timeseries.append({
                "date": m.date.isoformat(),
                "value": m.engagement
            })
        # Score
        if score:
            social_score["overall"] = score.overall_score
            social_score["submetrics"] = {
                "engagement": score.engagement_score,
                "reach": score.reach_score,
                "growth": score.growth_score
            }
            # Histórico de scores
            history_scores = SocialPageScore.query.filter_by(social_page_id=page.id).order_by(SocialPageScore.date.asc()).all()
            social_score["history"] = [
                {"date": s.date.isoformat(), "score": s.overall_score} for s in history_scores
            ]
    return jsonify({
        "success": True,
        "message": "Social account metrics retrieved successfully",
        "platforms": platforms,
        "engagementTimeseries": engagement_timeseries,
        "socialScore": social_score
    }), 200