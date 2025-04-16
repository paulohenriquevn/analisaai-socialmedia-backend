"""
Routes for relevance score metrics.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta

from app.models import SocialPage, SocialPageScore
from app.services.score_service import ScoreService

# Create blueprint
bp = Blueprint('score', __name__)

logger = logging.getLogger(__name__)

@bp.route('/social/score', methods=['GET'])
@jwt_required()
def get_social_score():
    """
    Retorna pontuação social do usuário no formato padronizado.
    Parâmetros de query:
      - period (string, opcional)
      - profileId (número, opcional)
    """
    period = request.args.get('period')
    profile_id = request.args.get('profileId', type=int)
    if not profile_id:
        return jsonify({"status": "error", "message": "profileId é obrigatório"}), 400

    # Obter usuário autenticado
    current_user_id = get_jwt_identity()
    # Verifica se o social_page existe e pertence ao usuário
    social_page = SocialPage.query.filter_by(id=profile_id, user_id=current_user_id).first()
    if not social_page:
        return jsonify({"status": "error", "message": f"Social page com ID {profile_id} não encontrada ou sem permissão"}), 404

    # Determinar datas a partir do period (ex: "30d")
    start_date = None
    end_date = None
    if period:
        try:
            if period.endswith('d'):
                days = int(period[:-1])
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days)
        except Exception:
            return jsonify({"status": "error", "message": "Formato de period inválido. Use, por exemplo, '30d'"}), 400

    metrics = ScoreService.get_score_metrics(profile_id, start_date, end_date)
    if not metrics or len(metrics) == 0:
        return jsonify({"status": "error", "message": "Nenhum score encontrado para o perfil informado."}), 404

    # Pega o score mais recente
    metric = metrics[0]
    response = {
        "overall": metric.overall_score,
        "engagement": metric.engagement_score,
        "reach": metric.reach_score,
        "growth": metric.growth_score,
        "consistency": metric.consistency_score,
        "quality": metric.audience_quality_score
    }
    return jsonify(response)

@bp.route('/metrics/<int:social_page_id>', methods=['GET'])
@jwt_required()
def get_score_metrics(social_page_id):
    """
    Get relevance score metrics for a specific social_page.
    
    Optional query parameters:
    - start_date: Filter metrics after this date (YYYY-MM-DD)
    - end_date: Filter metrics before this date (YYYY-MM-DD)
    - period: Predefined period (last_week, last_month, last_3_months, last_year)
    """
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Check if social_page exists and belongs to the current user
    social_page = SocialPage.query.filter_by(id=social_page_id, user_id=current_user_id).first()
    if not social_page:
        return jsonify({
            "status": "error",
            "message": f"Social page with ID {social_page_id} not found or you don't have permission to access it"
        }), 404
    
    # Parse date parameters
    start_date = None
    end_date = None
    
    # If period is specified, calculate date range
    period = request.args.get('period')
    if period:
        today = datetime.now().date()
        
        if period == 'last_week':
            start_date = today - timedelta(days=7)
        elif period == 'last_month':
            start_date = today - timedelta(days=30)
        elif period == 'last_3_months':
            start_date = today - timedelta(days=90)
        elif period == 'last_year':
            start_date = today - timedelta(days=365)
    else:
        # Parse custom date range
        if 'start_date' in request.args:
            try:
                start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid start_date format. Use YYYY-MM-DD"
                }), 400
                
        if 'end_date' in request.args:
            try:
                end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid end_date format. Use YYYY-MM-DD"
                }), 400
    
    # Get metrics from database
    metrics = ScoreService.get_score_metrics(social_page_id, start_date, end_date)
    
    # Format response
    result = []
    for metric in metrics:
        result.append({
            "date": metric.date.isoformat() if metric.date else None,
            "overall_score": metric.overall_score,
            "engagement_score": metric.engagement_score,
            "reach_score": metric.reach_score,
            "growth_score": metric.growth_score,
            "consistency_score": metric.consistency_score,
            "audience_quality_score": metric.audience_quality_score,
            "engagement_weight": metric.engagement_weight,
            "reach_weight": metric.reach_weight,
            "growth_weight": metric.growth_weight,
            "consistency_weight": metric.consistency_weight,
            "audience_quality_weight": metric.audience_quality_weight
        })
    
    return jsonify({
        "status": "success",
        "social_page": {
            "id": social_page.id,
            "username": social_page.username,
            "platform": social_page.platform,
            "relevance_score": social_page.relevance_score
        },
        "metrics": result
    })

@bp.route('/calculate/<int:social_page_id>', methods=['POST'])
@jwt_required()
def calculate_score(social_page_id):
    """Calculate and save relevance score for an social_page."""
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Check if social_page exists and belongs to the current user
    social_page = SocialPage.query.filter_by(id=social_page_id, user_id=current_user_id).first()
    if not social_page:
        return jsonify({
            "status": "error",
            "message": f"Social page with ID {social_page_id} not found or you don't have permission to access it"
        }), 404
    
    # Calculate metrics
    metrics = ScoreService.calculate_relevance_score(social_page_id)
    
    if not metrics:
        return jsonify({
            "status": "error",
            "message": "Failed to calculate relevance score"
        }), 500
    
    # Format date for response
    if 'date' in metrics and hasattr(metrics['date'], 'isoformat'):
        metrics['date'] = metrics['date'].isoformat()
    
    return jsonify({
        "status": "success",
        "message": "Relevance score calculated successfully",
        "score": {
            "overall_score": metrics['overall_score'],
            "engagement_score": metrics['engagement_score'],
            "reach_score": metrics['reach_score'],
            "growth_score": metrics['growth_score'],
            "consistency_score": metrics['consistency_score'],
            "audience_quality_score": metrics['audience_quality_score']
        },
        "current_relevance_score": social_page.relevance_score
    })

@bp.route('/calculate-all', methods=['POST'])
@jwt_required()
def calculate_all_scores():
    """Calculate relevance scores for all social pages owned by the current user."""
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Calculate metrics for all social pages owned by the current user
    results = ScoreService.calculate_all_social_pages_scores(current_user_id)
    
    return jsonify({
        "status": "success",
        "message": f"Relevance score calculation completed: {results['success']} succeeded, {results['failed']} failed",
        "results": results
    })

@bp.route('/compare', methods=['GET'])
@jwt_required()
def compare_scores():
    """
    Compare relevance scores of multiple social_pages.
    
    Required query parameters:
    - social_page_ids: Comma-separated list of social_page IDs to compare
    """
    # Get current user
    current_user_id = get_jwt_identity()
    
    # Get social_page IDs from request
    social_page_ids_param = request.args.get('social_page_ids')
    if not social_page_ids_param:
        return jsonify({
            "status": "error",
            "message": "Missing required parameter: social_page_ids"
        }), 400
    
    # Parse social_page IDs
    try:
        social_page_ids = [int(id_str) for id_str in social_page_ids_param.split(',')]
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid social_page_ids format. Must be comma-separated integers."
        }), 400
    
    # Get social_pages with their scores
    social_pages = SocialPage.query.filter(SocialPage.id.in_(social_page_ids)).all()
    
    # Format response
    result = []
    for social_page in social_pages:
        # Get most recent score metrics (returns already ordered by date descending)
        score_metrics = ScoreService.get_score_metrics(social_page.id)
        # Take only the most recent entry if available
        if score_metrics:
            score_metrics = score_metrics[:1]
        score_details = None
        
        if score_metrics:
            metric = score_metrics[0]
            score_details = {
                "overall_score": metric.overall_score,
                "engagement_score": metric.engagement_score,
                "reach_score": metric.reach_score,
                "growth_score": metric.growth_score,
                "consistency_score": metric.consistency_score,
                "audience_quality_score": metric.audience_quality_score,
                "last_calculated": metric.date.isoformat() if metric.date else None
            }
        
        result.append({
            "id": social_page.id,
            "username": social_page.username,
            "platform": social_page.platform,
            "relevance_score": social_page.relevance_score,
            "score_details": score_details
        })
    
    # Sort by overall score (highest first)
    result.sort(key=lambda x: x['relevance_score'] if x['relevance_score'] is not None else 0, reverse=True)
    
    return jsonify({
        "status": "success",
        "comparison": result
    })