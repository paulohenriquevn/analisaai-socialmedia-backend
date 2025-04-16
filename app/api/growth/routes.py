import logging
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

bp = Blueprint('growth-goals', __name__)
logger = logging.getLogger(__name__)


@bp.route('/', methods=['POST'])
@jwt_required()
def post_growth_goals():
    from common.social_media import SocialPageGrowth
    from app.extensions import db
    user_id = int(get_jwt_identity())
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of growth goals"}), 400
    created_goals = []
    for goal in data:
        if not all(k in goal for k in ("platform", "followersGoal")):
            return jsonify({"error": "Missing required fields in one or more goals"}), 400
        new_goal = SocialPageGrowth(
            user_id=user_id,
            platform=goal["platform"],
            followers_goal=goal["followersGoal"],
            engagement_goal=goal.get("engagementGoal"),
            deadline=goal.get("deadline"),
            is_goal=True
        )
        db.session.add(new_goal)
        created_goals.append(new_goal)
    db.session.commit()
    # Retorna todas as metas do usuário
    user_goals = SocialPageGrowth.query.filter_by(user_id=user_id, is_goal=True).all()
    return jsonify({
        "success": True,
        "message": "Growth goals updated successfully",
        "data": [
            {
                "id": g.id,
                "platform": g.platform,
                "followersGoal": g.followers_goal,
                "engagementGoal": g.engagement_goal,
                "deadline": g.deadline.isoformat() if g.deadline else None
            } for g in user_goals
        ]
    }), 201


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_growth_goal(id):
    from common.social_media import SocialPageGrowth
    from app.extensions import db
    user_id = int(get_jwt_identity())
    goal = SocialPageGrowth.query.filter_by(id=id, user_id=user_id, is_goal=True).first()
    if not goal:
        return jsonify({"error": "Growth goal not found"}), 404
    db.session.delete(goal)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Growth goal deleted successfully"
    }), 200


@bp.route('/metrics/basic', methods=['GET'])
@jwt_required()
def get_growth_goals():
    user_id = int(get_jwt_identity())
    goals = SocialPageGrowth.query.filter_by(user_id=user_id, is_goal=True).all()
    return jsonify({
        "success": True,
        "message": "Growth goals retrieved successfully",
        "data": [
            {
                "id": g.id,
                "platform": g.platform,
                "followersGoal": g.followers_goal,
                "engagementGoal": g.engagement_goal,
                "deadline": g.deadline.isoformat() if g.deadline else None
            } for g in goals
        ]
    }), 200