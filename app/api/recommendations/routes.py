import logging
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

bp = Blueprint('recommendations', __name__)
logger = logging.getLogger(__name__)


@bp.route('/content-ideas', methods=['GET'])
@jwt_required()
def get_content_ideas():
    from flask import request
    from common.recommendations import ContentIdea, SavedContentIdea
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    logger.info(f"[get_content_ideas] User {user_id} requested content ideas page={page} per_page={per_page}")
    try:
        ideas_pagination = ContentIdea.query.order_by(ContentIdea.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        ideas = ideas_pagination.items
        saved_ids = {s.idea_id for s in SavedContentIdea.query.filter_by(user_id=user_id).all()}
        data = []
    except Exception as e:
        logger.error(f"[get_content_ideas] Error for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
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
    return jsonify({
        "success": True,
        "message": "Content ideas retrieved successfully",
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": ideas_pagination.total,
            "total_pages": ideas_pagination.pages
        }
    }), 200


@bp.route('/content-ideas/save', methods=['POST'])
@jwt_required()
def save_content_idea():
    from common.recommendations import SavedContentIdea
    from app.extensions import db
    from app.schemas.recommendation import SaveContentIdeaSchema
    user_id = int(get_jwt_identity())
    data = request.json or {}
    errors = SaveContentIdeaSchema().validate(data)
    if errors:
        return jsonify({"error": "Validation error", "messages": errors}), 400
    idea_id = data.get('ideaId')
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
    from flask import request
    from common.recommendations import ContentIdea, SavedContentIdea
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    logger.info(f"[get_saved_content_ideas] User {user_id} requested saved content ideas page={page} per_page={per_page}")
    try:
        saved = SavedContentIdea.query.filter_by(user_id=user_id)
        idea_ids = [s.idea_id for s in saved]
        query = ContentIdea.query.filter(ContentIdea.id.in_(idea_ids)) if idea_ids else ContentIdea.query.filter(False)
        ideas_pagination = query.order_by(ContentIdea.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        ideas = ideas_pagination.items
        data = []
    except Exception as e:
        logger.error(f"[get_saved_content_ideas] Error for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
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
    return jsonify({
        "success": True,
        "message": "Saved content ideas retrieved successfully",
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": ideas_pagination.total,
            "total_pages": ideas_pagination.pages
        }
    }), 200


@bp.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar():
    from flask import request
    from common.recommendations import CalendarPost
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    logger.info(f"[get_calendar] User {user_id} requested calendar page={page} per_page={per_page}")
    try:
        posts_pagination = CalendarPost.query.filter_by(user_id=user_id).order_by(CalendarPost.date).paginate(page=page, per_page=per_page, error_out=False)
        posts = posts_pagination.items
        data = []
    except Exception as e:
        logger.error(f"[get_calendar] Error for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    for post in posts:
        data.append({
            "id": post.id,
            "date": post.date.isoformat() if post.date else None,
            "platform": post.platform,
            "contentTitle": post.content_title,
            "contentType": post.content_type,
            "status": post.status
        })
    return jsonify({
        "success": True,
        "message": "Calendar retrieved successfully",
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": posts_pagination.total,
            "total_pages": posts_pagination.pages
        }
    }), 200

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
    from flask import request
    from common.recommendations import Trend
    platform = request.args.get('platform')
    query = Trend.query
    if platform:
        query = query.filter(Trend.platforms.contains(platform))
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    logger.info(f"[get_trends] Trends requested page={page} per_page={per_page} platform={platform}")
    try:
        trends_pagination = query.order_by(Trend.popularity.desc(), Trend.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        trends = trends_pagination.items
        data = []
    except Exception as e:
        logger.error(f"[get_trends] Error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
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
    return jsonify({
        "success": True,
        "message": "Trends retrieved successfully",
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": trends_pagination.total,
            "total_pages": trends_pagination.pages
        }
    }), 200
