"""
User-related routes.
"""
import logging
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.user import User

bp = Blueprint('users', __name__)
logger = logging.getLogger(__name__)



@bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    organizations = []
    if hasattr(user, 'organizations'):
        organizations = [{
            "id": org.id,
            "name": org.name,
            "plan": org.plan.name if hasattr(org, 'plan') and org.plan else None
        } for org in user.organizations]
    
    return jsonify({
        "success": True,
        "message": "User profile retrieved successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "onboarding_completed": user.onboarding_completed,
            "created_at": user.created_at.isoformat(),
            "organizations": organizations,
            "profile_image": user.profile_image
        }
    }), 200


@bp.route('/me', methods=['PUT'])
def put_me():
    user_id = int(get_jwt_identity())
    logger.info(f"[put_me] User {user_id} requested profile update")
    user = User.query.get(user_id)
    if not user:
        logger.warning(f"[put_me] User {user_id} not found")
        return jsonify({"error": "User not found"}), 404
    
    from app.schemas.user import UpdateUserSchema
    data = request.json or {}
    errors = UpdateUserSchema().validate(data)
    if errors:
        logger.warning(f"[put_me] Validation error for user {user_id}: {errors}")
        return jsonify({"error": "Validation error", "messages": errors}), 400
    user.name = data['name']
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Profile completed successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "onboarding_completed": user.onboarding_completed,
            "created_at": user.created_at.isoformat(),
            "organizations": organizations,
            "profile_image": user.profile_image
        }
    }), 201


@bp.route('/me/password', methods=['PUT'])
def put_me_password():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    from app.schemas.user import UpdatePasswordSchema
    data = request.json or {}
    errors = UpdatePasswordSchema().validate(data)
    if errors:
        return jsonify({"error": "Validation error", "messages": errors}), 400
    user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Password updated successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "onboarding_completed": user.onboarding_completed,
            "created_at": user.created_at.isoformat(),
            "organizations": organizations,
            "profile_image": user.profile_image
        }
    }), 201


@bp.route('/me/complete-onboarding', methods=['PUT'])
def put_me_complete_onboarding():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    from app.schemas.user import UpdateUserSchema
    data = request.json or {}
    errors = UpdateUserSchema().validate(data)
    if errors:
        return jsonify({"error": "Validation error", "messages": errors}), 400
    user.name = data['name']
    user.onboarding_completed = True
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Profile completed successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "onboarding_completed": user.onboarding_completed,
            "created_at": user.created_at.isoformat(),
            "organizations": organizations,
            "profile_image": user.profile_image
        }
    }), 201