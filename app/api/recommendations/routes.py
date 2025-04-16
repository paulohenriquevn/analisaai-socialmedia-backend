import logging
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

bp = Blueprint('recommendations', __name__)
logger = logging.getLogger(__name__)


@bp.route('/content-ideas', methods=['GET'])
@jwt_required()
def get_content_ideas():
    from common.recommendations import ContentIdea, SavedContentIdea
    user_id = int(get_jwt_identity())
    ideas = ContentIdea.query.all()
    saved_ids = {s.idea_id for s in SavedContentIdea.query.filter_by(user_id=user_id).all()}
    data = []
    for idea in ideas:
        data.append({
            "id": idea.id,
            "title": idea.title,
            "description": idea.description,
            "platforms": idea.platforms.split(',') if idea.platforms else [],
            "contentType": idea.content_type,
            "tags": idea.tags.split(',') if idea.tags else [],
            "estimatedEngagement": idea.estimated_engagement,
            "createdAt": idea.created_at.isoformat() if idea.created_at else None,
            "isSaved": idea.id in saved_ids
        })
    return jsonify({"success": True, "message": "Content ideas retrieved successfully", "data": data}), 200


@bp.route('/content-ideas/save', methods=['POST'])
@jwt_required()
def save_content_idea():
    from common.recommendations import SavedContentIdea
    from app.extensions import db
    user_id = int(get_jwt_identity())
    data = request.json
    idea_id = data.get('ideaId')
    if not idea_id:
        return jsonify({"error": "Missing ideaId"}), 400
    exists = SavedContentIdea.query.filter_by(user_id=user_id, idea_id=idea_id).first()
    if not exists:
        saved = SavedContentIdea(user_id=user_id, idea_id=idea_id)
        db.session.add(saved)
        db.session.commit()
    return jsonify({
        "success": True,
        "message": "Content idea saved successfully",
        "data": {"ideaId": idea_id, "isSaved": True}
    }), 200


@bp.route('/content-ideas/saved', methods=['GET'])
@jwt_required()
def get_saved_content_ideas():
    from common.recommendations import ContentIdea, SavedContentIdea
    user_id = int(get_jwt_identity())
    saved = SavedContentIdea.query.filter_by(user_id=user_id).all()
    idea_ids = [s.idea_id for s in saved]
    ideas = ContentIdea.query.filter(ContentIdea.id.in_(idea_ids)).all() if idea_ids else []
    data = []
    for idea in ideas:
        data.append({
            "id": idea.id,
            "title": idea.title,
            "description": idea.description,
            "platforms": idea.platforms.split(',') if idea.platforms else [],
            "contentType": idea.content_type,
            "tags": idea.tags.split(',') if idea.tags else [],
            "estimatedEngagement": idea.estimated_engagement,
            "createdAt": idea.created_at.isoformat() if idea.created_at else None,
            "isSaved": True
        })
    return jsonify({"success": True, "message": "Saved content ideas retrieved successfully", "data": data}), 200


@bp.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar():
    from common.recommendations import CalendarPost
    user_id = int(get_jwt_identity())
    posts = CalendarPost.query.filter_by(user_id=user_id).order_by(CalendarPost.date).all()
    data = []
    for post in posts:
        data.append({
            "id": post.id,
            "date": post.date.isoformat() if post.date else None,
            "platform": post.platform,
            "contentTitle": post.content_title,
            "contentType": post.content_type,
            "status": post.status
        })
    return jsonify({"success": True, "message": "Calendar retrieved successfully", "data": data}), 200

@bp.route('/optimization', methods=['GET'])
@jwt_required()
def get_optimization():
    from common.recommendations import OptimizationTip
    platform = flask.request.args.get('platform')
    query = OptimizationTip.query
    if platform:
        query = query.filter_by(platform=platform)
    tips = query.order_by(OptimizationTip.created_at.desc()).all()
    data = []
    for tip in tips:
        data.append({
            "id": tip.id,
            "platform": tip.platform,
            "title": tip.title,
            "description": tip.description,
            "impact": tip.impact,
            "bestPractices": tip.best_practices.split(';') if tip.best_practices else []
        })
    return jsonify({"success": True, "message": "Optimization tips retrieved successfully", "data": data}), 200

@bp.route('/trends', methods=['GET'])
@jwt_required()
def get_trends():
    from common.recommendations import Trend
    platform = flask.request.args.get('platform')
    query = Trend.query
    if platform:
        query = query.filter(Trend.platforms.contains(platform))
    trends = query.order_by(Trend.popularity.desc(), Trend.created_at.desc()).all()
    data = []
    for trend in trends:
        data.append({
            "id": trend.id,
            "title": trend.title,
            "description": trend.description,
            "popularity": trend.popularity,
            "platforms": trend.platforms.split(',') if trend.platforms else [],
            "hashtags": trend.hashtags.split(',') if trend.hashtags else [],
            "relatedTopics": trend.related_topics.split(',') if trend.related_topics else [],
            "createdAt": trend.created_at.isoformat() if trend.created_at else None
        })
    return jsonify({"success": True, "message": "Trends retrieved successfully", "data": data}), 200
