"""
Service for calculating and processing engagement metrics for influencers.
"""
import logging
from datetime import datetime, date, timedelta
from app.extensions import db
from app.models.influencer import Influencer, InfluencerMetric
from app.models.engagement import InfluencerEngagement

logger = logging.getLogger(__name__)

class EngagementService:
    """Service for calculating and tracking engagement metrics."""
    
    @staticmethod
    def calculate_engagement_metrics(influencer_id):
        """
        Calculate engagement metrics for a specific influencer.
        
        Args:
            influencer_id: ID of the influencer to calculate metrics for
            
        Returns:
            dict: The calculated engagement metrics or None if error
        """
        try:
            logger.info(f"Calculating engagement metrics for influencer ID: {influencer_id}")
            
            # Get the influencer
            influencer = Influencer.query.get(influencer_id)
            if not influencer:
                logger.error(f"Influencer with ID {influencer_id} not found")
                return None
                
            # Get latest metrics data
            latest_metric = InfluencerMetric.query.filter_by(
                influencer_id=influencer_id
            ).order_by(InfluencerMetric.date.desc()).first()
            
            if not latest_metric:
                logger.warning(f"No metrics data available for influencer {influencer_id}")
                
                # Create basic metrics using the influencer data
                engagement_metrics = {
                    'influencer_id': influencer_id,
                    'date': date.today(),
                    'posts_count': influencer.posts_count or 0,
                    'engagement_rate': influencer.engagement_rate or 0.0,
                    'total_likes': 0,
                    'total_comments': 0,
                    'total_shares': 0,
                    'avg_likes_per_post': 0,
                    'avg_comments_per_post': 0,
                    'avg_shares_per_post': 0,
                    'growth_rate': 0.0
                }
            else:
                # Use the metrics data to calculate engagement
                posts_count = latest_metric.posts or influencer.posts_count or 0
                
                # Calculate average metrics per post
                avg_likes = latest_metric.likes / posts_count if posts_count > 0 and latest_metric.likes else 0
                avg_comments = latest_metric.comments / posts_count if posts_count > 0 and latest_metric.comments else 0
                avg_shares = latest_metric.shares / posts_count if posts_count > 0 and latest_metric.shares else 0
                
                # Calculate follower growth rate
                previous_metric = InfluencerMetric.query.filter(
                    InfluencerMetric.influencer_id == influencer_id,
                    InfluencerMetric.date < latest_metric.date
                ).order_by(InfluencerMetric.date.desc()).first()
                
                growth_rate = 0.0
                if previous_metric and previous_metric.followers > 0:
                    growth_rate = ((latest_metric.followers - previous_metric.followers) / previous_metric.followers) * 100
                
                # Create engagement metrics dict
                engagement_metrics = {
                    'influencer_id': influencer_id,
                    'date': latest_metric.date,
                    'posts_count': posts_count,
                    'engagement_rate': latest_metric.engagement or influencer.engagement_rate or 0.0,
                    'total_likes': latest_metric.likes or 0,
                    'total_comments': latest_metric.comments or 0,
                    'total_shares': latest_metric.shares or 0,
                    'avg_likes_per_post': avg_likes,
                    'avg_comments_per_post': avg_comments,
                    'avg_shares_per_post': avg_shares,
                    'growth_rate': growth_rate,
                    'video_views': latest_metric.views or 0,
                }
                
                # Add platform-specific metrics if available
                if hasattr(latest_metric, 'impressions'):
                    engagement_metrics['impressions'] = latest_metric.impressions or 0
                if hasattr(latest_metric, 'reach'):
                    engagement_metrics['reach'] = latest_metric.reach or 0
            
            # Save the engagement metrics
            result = EngagementService.save_engagement_metrics(engagement_metrics)
            logger.info(f"Saved engagement metrics for influencer {influencer_id}")
            
            return engagement_metrics
            
        except Exception as e:
            logger.error(f"Error calculating engagement metrics for influencer {influencer_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def save_engagement_metrics(metrics_data):
        """
        Save engagement metrics to the database.
        
        Args:
            metrics_data: Dict containing engagement metrics
            
        Returns:
            InfluencerEngagement: Saved engagement record or None if error
        """
        try:
            # Check if metrics for this influencer and date already exist
            existing = InfluencerEngagement.query.filter_by(
                influencer_id=metrics_data['influencer_id'],
                date=metrics_data['date']
            ).first()
            
            if existing:
                # Update existing metrics
                for key, value in metrics_data.items():
                    if key != 'influencer_id' and key != 'date' and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                engagement = existing
            else:
                # Create new metrics record
                engagement = InfluencerEngagement(**metrics_data)
                db.session.add(engagement)
            
            db.session.commit()
            return engagement
            
        except Exception as e:
            logger.error(f"Error saving engagement metrics: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_engagement_metrics(influencer_id, start_date=None, end_date=None):
        """
        Get engagement metrics for an influencer within a date range.
        
        Args:
            influencer_id: ID of the influencer
            start_date: Start date for metrics (optional)
            end_date: End date for metrics (optional)
            
        Returns:
            list: List of engagement metrics or empty list if none found
        """
        query = InfluencerEngagement.query.filter_by(influencer_id=influencer_id)
        
        if start_date:
            query = query.filter(InfluencerEngagement.date >= start_date)
        
        if end_date:
            query = query.filter(InfluencerEngagement.date <= end_date)
        
        # Order by date (most recent first)
        query = query.order_by(InfluencerEngagement.date.desc())
        
        return query.all()
    
    @staticmethod
    def calculate_all_influencers_metrics():
        """
        Calculate engagement metrics for all influencers.
        
        Returns:
            dict: Summary of the calculation results
        """
        influencers = Influencer.query.all()
        results = {
            'total': len(influencers),
            'success': 0,
            'failed': 0
        }
        
        for influencer in influencers:
            try:
                metrics = EngagementService.calculate_engagement_metrics(influencer.id)
                if metrics:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception:
                results['failed'] += 1
        
        return results