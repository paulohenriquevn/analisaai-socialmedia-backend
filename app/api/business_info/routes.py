import logging
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

bp = Blueprint('businessinfo', __name__)
logger = logging.getLogger(__name__)


@bp.route('/', methods=['POST'])
@jwt_required()
def post_business_info():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    
    if 'name' in data:
        user.name = data['name']
    if 'industry' in data:
        user.industry = data['industry']
    if 'size' in data:
        user.size = data['size']
    if 'website' in data:
        user.website = data['website']
    if 'targetAudience' in data:
        user.target_audience = data['targetAudience']
    if 'objectives' in data:
        user.objectives = data['objectives']
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "User profile updated successfully",
        "business_info": {
            "name": user.name,
            "industry": user.industry,
            "size": user.size,
            "website": user.website,
            "targetAudience": user.target_audience if user.target_audience else [],
            "objectives": user.objectives if user.objectives else []
        }
    }), 200


@bp.route('/', methods=['POST'])
@jwt_required()
def post_social_accounts():
    from common.social_media import SocialPage
    from app.extensions import db
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
    from common.social_media import SocialPage
    from app.extensions import db
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
    from common.social_media import SocialPage, SocialPageMetric, SocialPageScore
    user_id = int(get_jwt_identity())
    pages = SocialPage.query.filter_by(user_id=user_id).all()
    platforms = []
    engagement_timeseries = []
    social_score = {
        "overall": 0,
        "submetrics": {"engagement": 0, "reach": 0, "growth": 0},
        "history": []
    }
    for page in pages:
        metric = SocialPageMetric.query.filter_by(social_page_id=page.id).order_by(SocialPageMetric.date.desc()).first()
        score = SocialPageScore.query.filter_by(social_page_id=page.id).order_by(SocialPageScore.date.desc()).first()
        platforms.append({
            "platform": page.platform,
            "followers": metric.followers if metric else 0,
            "engagement": metric.engagement if metric else 0,
            "impressions": getattr(metric, 'impressions', 0) if metric else 0,
            "reach": getattr(metric, 'reach', 0) if metric else 0,
            "growth": 0
        })
        metrics = SocialPageMetric.query.filter_by(social_page_id=page.id).order_by(SocialPageMetric.date.asc()).all()
        for m in metrics:
            engagement_timeseries.append({
                "date": m.date.isoformat(),
                "value": m.engagement
            })
        if score:
            social_score["overall"] = score.overall_score
            social_score["submetrics"] = {
                "engagement": score.engagement_score,
                "reach": score.reach_score,
                "growth": score.growth_score
            }
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