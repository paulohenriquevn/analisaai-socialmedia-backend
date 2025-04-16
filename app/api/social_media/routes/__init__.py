"""Social media routes."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import SocialPage, SocialPagePost

bp = Blueprint('social_media', __name__)

@bp.route('/social/posts', methods=['GET'])
@jwt_required()
def get_social_posts():
    """
    Recupera posts publicados nas redes conectadas.
    Parâmetros de query:
      - limit (número, padrão: 10)
      - offset (número, padrão: 0)
      - profileId (número, opcional)
    """
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    profile_id = request.args.get('profileId', type=int)
    user_id = get_jwt_identity()

    query = SocialPagePost.query
    if profile_id:
        # Verifica se o social_page pertence ao usuário
        page = SocialPage.query.filter_by(id=profile_id, user_id=user_id).first()
        if not page:
            return jsonify({"status": "error", "message": "Social page não encontrada ou sem permissão"}), 404
        query = query.filter_by(social_page_id=profile_id)
    else:
        # Listar posts de todas as páginas do usuário
        user_pages = SocialPage.query.filter_by(user_id=user_id).all()
        user_page_ids = [p.id for p in user_pages]
        query = query.filter(SocialPagePost.social_page_id.in_(user_page_ids))

    posts = query.order_by(SocialPagePost.posted_at.desc()).offset(offset).limit(limit).all()

    result = []
    for post in posts:
        result.append({
            "id": post.id,
            "platform": post.platform,
            "postUrl": post.post_url,
            "imageUrl": post.media_url,
            "caption": post.content,
            "likes": post.likes_count or 0,
            "comments": post.comments_count or 0,
            "shares": post.shares_count or 0,
            "impressions": post.views_count or 0,
            "reach": None,  # Campo não mapeado diretamente
            "engagement": post.engagement,
            "publishedAt": post.posted_at.isoformat() if post.posted_at else None,
            "type": post.content_type
        })
    return jsonify(result)
