"""
Service for preparing visualization data from metrics.
"""
import logging
from datetime import datetime, date, timedelta
import numpy as np
from app.models import (
    SocialPage,
    SocialPageEngagement,
    SocialPageReach,
    SocialPageGrowth,
    SocialPageScore,
)

logger = logging.getLogger(__name__)

class VisualizationService:
    """Service for generating visualization data for dashboards."""
    
    @staticmethod
    def get_engagement_visualization(social_page_id, time_range=30):
        """
        Get engagement metrics formatted for visualization.
        
        Args:
            social_page_id: ID of the social_page
            time_range: Number of days to include (default: 30)
            
        Returns:
            dict: Engagement visualization data
        """
        try:
            # Get the social_page
            social_page = SocialPage.query.get(social_page_id)
            if not social_page:
                logger.error(f"social_page with ID {social_page_id} not found")
                return None
            
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=time_range)
            
            # Get engagement metrics for the date range
            engagement_metrics = SocialPageEngagement.query.filter(
                SocialPageEngagement.social_page_id == social_page_id,
                SocialPageEngagement.date >= start_date,
                SocialPageEngagement.date <= end_date
            ).order_by(SocialPageEngagement.date.asc()).all()
            
            # Prepare data for visualization
            dates = []
            engagement_rates = []
            avg_likes = []
            avg_comments = []
            avg_shares = []
            total_likes = []
            total_comments = []
            
            for metric in engagement_metrics:
                dates.append(metric.date.isoformat())
                engagement_rates.append(metric.engagement_rate)
                avg_likes.append(metric.avg_likes_per_post)
                avg_comments.append(metric.avg_comments_per_post)
                avg_shares.append(metric.avg_shares_per_post)
                total_likes.append(metric.total_likes)
                total_comments.append(metric.total_comments)
            
            # Calculate additional insights
            average_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
            engagement_trend = VisualizationService._calculate_trend(engagement_rates)
            
            # Prepare the visualization data
            visualization_data = {
                "time_series": {
                    "dates": dates,
                    "engagement_rates": engagement_rates,
                    "avg_likes_per_post": avg_likes,
                    "avg_comments_per_post": avg_comments,
                    "avg_shares_per_post": avg_shares,
                    "total_likes": total_likes,
                    "total_comments": total_comments
                },
                "insights": {
                    "average_engagement": average_engagement,
                    "engagement_trend": engagement_trend,
                    "most_engaged_date": dates[engagement_rates.index(max(engagement_rates))] if engagement_rates else None,
                    "least_engaged_date": dates[engagement_rates.index(min(engagement_rates))] if engagement_rates else None
                },
                "metadata": {
                    "social_page_id": social_page_id,
                    "platform": social_page.platform,
                    "username": social_page.username,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "time_range_days": time_range
                }
            }
            
            return visualization_data
            
        except Exception as e:
            logger.error(f"Error generating engagement visualization for social_page {social_page_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def get_reach_visualization(social_page_id, time_range=30):
        """
        Get reach metrics formatted for visualization.
        
        Args:
            social_page_id: ID of the social_page
            time_range: Number of days to include (default: 30)
            
        Returns:
            dict: Reach visualization data
        """
        try:
            # Get the social_page
            social_page = SocialPage.query.get(social_page_id)
            if not social_page:
                logger.error(f"social_page with ID {social_page_id} not found")
                return None
            
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=time_range)
            
            # Get reach metrics for the date range
            reach_metrics = SocialPageReach.query.filter(
                SocialPageReach.social_page_id == social_page_id,
                SocialPageReach.date >= start_date,
                SocialPageReach.date <= end_date
            ).order_by(SocialPageReach.date.asc()).all()
            
            # Prepare data for visualization
            dates = []
            impressions = []
            reach_values = []
            story_views = []
            profile_views = []
            audience_growth_vals = []
            
            for metric in reach_metrics:
                dates.append(metric.date.isoformat())
                impressions.append(metric.impressions)
                reach_values.append(metric.reach)
                story_views.append(metric.story_views)
                profile_views.append(metric.profile_views)
                audience_growth_vals.append(metric.audience_growth)
            
            # Calculate additional insights
            average_reach = sum(reach_values) / len(reach_values) if reach_values else 0
            reach_trend = VisualizationService._calculate_trend(reach_values)
            
            # Calculate impressions-to-reach ratio
            impressions_to_reach_ratio = []
            for i in range(len(impressions)):
                if reach_values[i] > 0:
                    impressions_to_reach_ratio.append(impressions[i] / reach_values[i])
                else:
                    impressions_to_reach_ratio.append(0)
            
            # Prepare the visualization data
            visualization_data = {
                "time_series": {
                    "dates": dates,
                    "impressions": impressions,
                    "reach": reach_values,
                    "story_views": story_views,
                    "profile_views": profile_views,
                    "audience_growth": audience_growth_vals,
                    "impressions_to_reach_ratio": impressions_to_reach_ratio
                },
                "insights": {
                    "average_reach": average_reach,
                    "reach_trend": reach_trend,
                    "peak_impressions": max(impressions) if impressions else 0,
                    "peak_reach": max(reach_values) if reach_values else 0,
                    "avg_impressions_to_reach_ratio": sum(impressions_to_reach_ratio) / len(impressions_to_reach_ratio) if impressions_to_reach_ratio else 0
                },
                "metadata": {
                    "social_page_id": social_page_id,
                    "platform": social_page.platform,
                    "username": social_page.username,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "time_range_days": time_range
                }
            }
            
            return visualization_data
            
        except Exception as e:
            logger.error(f"Error generating reach visualization for social_page {social_page_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def get_growth_visualization(social_page_id, time_range=30):
        """
        Get growth metrics formatted for visualization.
        
        Args:
            social_page_id: ID of the social_page
            time_range: Number of days to include (default: 30)
            
        Returns:
            dict: Growth visualization data
        """
        try:
            # Get the social_page
            social_page = SocialPage.query.get(social_page_id)
            if not social_page:
                logger.error(f"social_page with ID {social_page_id} not found")
                return None
            
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=time_range)
            
            # Get growth metrics for the date range
            growth_metrics = SocialPageGrowth.query.filter(
                SocialPageGrowth.social_page_id == social_page_id,
                SocialPageGrowth.date >= start_date,
                SocialPageGrowth.date <= end_date
            ).order_by(SocialPageGrowth.date.asc()).all()
            
            # Prepare data for visualization
            dates = []
            followers_counts = []
            new_followers_daily = []
            retention_rates = []
            daily_growth_rates = []
            growth_velocities = []
            
            for metric in growth_metrics:
                dates.append(metric.date.isoformat())
                followers_counts.append(metric.followers_count)
                new_followers_daily.append(metric.new_followers_daily)
                retention_rates.append(metric.retention_rate)
                daily_growth_rates.append(metric.daily_growth_rate)
                growth_velocities.append(metric.growth_velocity)
            
            # Calculate additional insights
            followers_trend = VisualizationService._calculate_trend(followers_counts)
            growth_rate_trend = VisualizationService._calculate_trend(daily_growth_rates)
            
            # Calculate cumulative growth
            if followers_counts and len(followers_counts) > 1:
                total_follower_gain = followers_counts[-1] - followers_counts[0]
                cumulative_growth_rate = ((followers_counts[-1] / followers_counts[0]) - 1) * 100 if followers_counts[0] > 0 else 0
            else:
                total_follower_gain = 0
                cumulative_growth_rate = 0
            
            # Prepare the visualization data
            visualization_data = {
                "time_series": {
                    "dates": dates,
                    "followers_count": followers_counts,
                    "new_followers_daily": new_followers_daily,
                    "retention_rate": retention_rates,
                    "daily_growth_rate": daily_growth_rates,
                    "growth_velocity": growth_velocities
                },
                "insights": {
                    "followers_trend": followers_trend,
                    "growth_rate_trend": growth_rate_trend,
                    "total_follower_gain": total_follower_gain,
                    "cumulative_growth_rate": cumulative_growth_rate,
                    "average_daily_growth_rate": sum(daily_growth_rates) / len(daily_growth_rates) if daily_growth_rates else 0,
                    "projected_followers_30d": followers_counts[-1] * (1 + (sum(daily_growth_rates) / len(daily_growth_rates) / 100)) ** 30 if followers_counts and daily_growth_rates else 0
                },
                "metadata": {
                    "social_page_id": social_page_id,
                    "platform": social_page.platform,
                    "username": social_page.username,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "time_range_days": time_range
                }
            }
            
            return visualization_data
            
        except Exception as e:
            logger.error(f"Error generating growth visualization for social_page {social_page_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def get_score_visualization(social_page_id, time_range=30):
        """
        Get score metrics formatted for visualization.
        
        Args:
            social_page_id: ID of the social_page
            time_range: Number of days to include (default: 30)
            
        Returns:
            dict: Score visualization data
        """
        try:
            # Get the social_page
            social_page = SocialPage.query.get(social_page_id)
            if not social_page:
                logger.error(f"social_page with ID {social_page_id} not found")
                return None
            
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=time_range)
            
            # Get score metrics for the date range
            score_metrics = SocialPageScore.query.filter(
                SocialPageScore.social_page_id == social_page_id,
                SocialPageScore.date >= start_date,
                SocialPageScore.date <= end_date
            ).order_by(SocialPageScore.date.asc()).all()
            
            # Prepare data for visualization
            dates = []
            overall_scores = []
            engagement_scores = []
            reach_scores = []
            growth_scores = []
            consistency_scores = []
            audience_quality_scores = []
            
            for metric in score_metrics:
                dates.append(metric.date.isoformat())
                overall_scores.append(metric.overall_score)
                engagement_scores.append(metric.engagement_score)
                reach_scores.append(metric.reach_score)
                growth_scores.append(metric.growth_score)
                consistency_scores.append(metric.consistency_score)
                audience_quality_scores.append(metric.audience_quality_score)
            
            # Calculate additional insights
            score_trend = VisualizationService._calculate_trend(overall_scores)
            
            # Get the most recent score breakdown
            if score_metrics:
                latest_metric = score_metrics[-1]
                score_breakdown = {
                    "engagement": {
                        "score": latest_metric.engagement_score,
                        "weight": latest_metric.engagement_weight,
                        "weighted_score": latest_metric.engagement_score * latest_metric.engagement_weight
                    },
                    "reach": {
                        "score": latest_metric.reach_score,
                        "weight": latest_metric.reach_weight,
                        "weighted_score": latest_metric.reach_score * latest_metric.reach_weight
                    },
                    "growth": {
                        "score": latest_metric.growth_score,
                        "weight": latest_metric.growth_weight,
                        "weighted_score": latest_metric.growth_score * latest_metric.growth_weight
                    },
                    "consistency": {
                        "score": latest_metric.consistency_score,
                        "weight": latest_metric.consistency_weight,
                        "weighted_score": latest_metric.consistency_score * latest_metric.consistency_weight
                    },
                    "audience_quality": {
                        "score": latest_metric.audience_quality_score,
                        "weight": latest_metric.audience_quality_weight,
                        "weighted_score": latest_metric.audience_quality_score * latest_metric.audience_quality_weight
                    }
                }
            else:
                score_breakdown = {}
            
            # Prepare the visualization data
            visualization_data = {
                "time_series": {
                    "dates": dates,
                    "overall_scores": overall_scores,
                    "engagement_scores": engagement_scores,
                    "reach_scores": reach_scores,
                    "growth_scores": growth_scores,
                    "consistency_scores": consistency_scores,
                    "audience_quality_scores": audience_quality_scores
                },
                "insights": {
                    "current_score": overall_scores[-1] if overall_scores else 0,
                    "score_trend": score_trend,
                    "best_performing_component": VisualizationService._get_best_component(score_breakdown) if score_breakdown else None,
                    "needs_improvement_component": VisualizationService._get_worst_component(score_breakdown) if score_breakdown else None,
                    "score_breakdown": score_breakdown
                },
                "metadata": {
                    "social_page_id": social_page_id,
                    "platform": social_page.platform,
                    "username": social_page.username,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "time_range_days": time_range
                }
            }
            
            return visualization_data
            
        except Exception as e:
            logger.error(f"Error generating score visualization for social_page {social_page_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def get_dashboard_overview(social_page_id):
        """
        Get a comprehensive overview of all metrics for the dashboard.
        
        Args:
            social_page_id: ID of the social_page
            
        Returns:
            dict: Dashboard overview data
        """
        try:
            # Get the social_page
            social_page = SocialPage.query.get(social_page_id)
            if not social_page:
                logger.error(f"social_page with ID {social_page_id} not found")
                return None
            
            # Get the latest metrics
            latest_engagement = SocialPageEngagement.query.filter_by(
                social_page_id=social_page_id
            ).order_by(SocialPageEngagement.date.desc()).first()
            
            latest_reach = SocialPageReach.query.filter_by(
                social_page_id=social_page_id
            ).order_by(SocialPageReach.date.desc()).first()
            
            latest_growth = SocialPageGrowth.query.filter_by(
                social_page_id=social_page_id
            ).order_by(SocialPageGrowth.date.desc()).first()
            
            latest_score = SocialPageScore.query.filter_by(
                social_page_id=social_page_id
            ).order_by(SocialPageScore.date.desc()).first()
            
            # Prepare the overview data
            overview_data = {
                "social_page": {
                    "id": social_page.id,
                    "username": social_page.username,
                    "platform": social_page.platform,
                    "full_name": social_page.full_name,
                    "profile_image": social_page.profile_image,
                    "followers_count": social_page.followers_count,
                    "following_count": social_page.following_count,
                    "posts_count": social_page.posts_count,
                    "engagement_rate": social_page.engagement_rate,
                    "relevance_score": social_page.relevance_score
                },
                "metrics_summary": {
                    "engagement": {
                        "engagement_rate": latest_engagement.engagement_rate if latest_engagement else 0,
                        "avg_likes_per_post": latest_engagement.avg_likes_per_post if latest_engagement else 0,
                        "avg_comments_per_post": latest_engagement.avg_comments_per_post if latest_engagement else 0,
                        "last_updated": latest_engagement.date.isoformat() if latest_engagement and latest_engagement.date else None
                    },
                    "reach": {
                        "impressions": latest_reach.impressions if latest_reach else 0,
                        "reach": latest_reach.reach if latest_reach else 0,
                        "story_views": latest_reach.story_views if latest_reach else 0,
                        "profile_views": latest_reach.profile_views if latest_reach else 0,
                        "last_updated": latest_reach.date.isoformat() if latest_reach and latest_reach.date else None
                    },
                    "growth": {
                        "new_followers_daily": latest_growth.new_followers_daily if latest_growth else 0,
                        "retention_rate": latest_growth.retention_rate if latest_growth else 0,
                        "daily_growth_rate": latest_growth.daily_growth_rate if latest_growth else 0,
                        "last_updated": latest_growth.date.isoformat() if latest_growth and latest_growth.date else None
                    },
                    "score": {
                        "overall_score": latest_score.overall_score if latest_score else 0,
                        "engagement_score": latest_score.engagement_score if latest_score else 0,
                        "reach_score": latest_score.reach_score if latest_score else 0,
                        "growth_score": latest_score.growth_score if latest_score else 0,
                        "consistency_score": latest_score.consistency_score if latest_score else 0,
                        "audience_quality_score": latest_score.audience_quality_score if latest_score else 0,
                        "last_updated": latest_score.date.isoformat() if latest_score and latest_score.date else None
                    }
                },
                "visualizations": {
                    "engagement": VisualizationService.get_engagement_visualization(social_page_id, 7),  # Last 7 days
                    "reach": VisualizationService.get_reach_visualization(social_page_id, 7),  # Last 7 days
                    "growth": VisualizationService.get_growth_visualization(social_page_id, 7),  # Last 7 days
                    "score": VisualizationService.get_score_visualization(social_page_id, 7)  # Last 7 days
                }
            }
            
            return overview_data
            
        except Exception as e:
            logger.error(f"Error generating dashboard overview for social_page {social_page_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def get_comparison_visualization(social_page_ids):
        """
        Get visualization data for comparing multiple social_pages.
        
        Args:
            social_page_ids: List of social_page IDs to compare
            
        Returns:
            dict: Comparison visualization data
        """
        try:
            # Get the social_pages
            social_pages = SocialPage.query.filter(SocialPage.id.in_(social_page_ids)).all()
            if not social_pages:
                logger.error(f"No social_pages found for IDs: {social_page_ids}")
                return None
            
            # Prepare data structure
            comparison_data = {
                "social_pages": [],
                "metrics_comparison": {
                    "followers_count": [],
                    "engagement_rate": [],
                    "reach": [],
                    "growth_rate": [],
                    "relevance_score": []
                }
            }
            
            # Gather data for each social_page
            for social_page in social_pages:
                # Add basic social_page info
                comparison_data["social_pages"].append({
                    "id": social_page.id,
                    "username": social_page.username,
                    "platform": social_page.platform,
                    "followers_count": social_page.followers_count,
                    "engagement_rate": social_page.engagement_rate,
                    "relevance_score": social_page.relevance_score
                })
                
                # Add metrics data for comparison
                comparison_data["metrics_comparison"]["followers_count"].append({
                    "name": social_page.username,
                    "value": social_page.followers_count
                })
                
                comparison_data["metrics_comparison"]["engagement_rate"].append({
                    "name": social_page.username,
                    "value": social_page.engagement_rate
                })
                
                comparison_data["metrics_comparison"]["relevance_score"].append({
                    "name": social_page.username,
                    "value": social_page.relevance_score
                })
                
                # Get more detailed metrics
                latest_reach = SocialPageReach.query.filter_by(
                    social_page_id=social_page.id
                ).order_by(SocialPageReach.date.desc()).first()
                
                latest_growth = SocialPageGrowth.query.filter_by(
                    social_page_id=social_page.id
                ).order_by(SocialPageGrowth.date.desc()).first()
                
                # Add reach and growth data if available
                reach_value = latest_reach.reach if latest_reach else 0
                comparison_data["metrics_comparison"]["reach"].append({
                    "name": social_page.username,
                    "value": reach_value
                })
                
                growth_rate = latest_growth.daily_growth_rate if latest_growth else 0
                comparison_data["metrics_comparison"]["growth_rate"].append({
                    "name": social_page.username,
                    "value": growth_rate
                })
            
            return comparison_data
            
        except Exception as e:
            logger.error(f"Error generating comparison visualization for social_pages {social_page_ids}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def _calculate_trend(values):
        """
        Calculate the trend of a sequence of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            dict: Trend information
        """
        if not values or len(values) < 2:
            return {
                "direction": "neutral",
                "change_percent": 0,
                "slope": 0
            }
        
        # Calculate simple trend indicators
        start_value = values[0]
        end_value = values[-1]
        
        if start_value == 0:
            change_percent = 0 if end_value == 0 else 100  # Avoid division by zero
        else:
            change_percent = ((end_value - start_value) / start_value) * 100
        
        # Determine direction
        if change_percent > 0:
            direction = "up"
        elif change_percent < 0:
            direction = "down"
        else:
            direction = "neutral"
        
        # Calculate slope using linear regression for more accurate trend
        if len(values) > 2:
            try:
                x = np.array(range(len(values)))
                y = np.array(values)
                slope, _ = np.polyfit(x, y, 1)
            except:
                slope = 0
        else:
            slope = end_value - start_value
        
        return {
            "direction": direction,
            "slope": slope
        }
    
    @staticmethod
    def _get_best_component(score_breakdown):
        """Get the best performing component from score breakdown."""
        if not score_breakdown:
            return None
        
        max_score = 0
        best_component = None
        
        for component, data in score_breakdown.items():
            if data["weighted_score"] > max_score:
                max_score = data["weighted_score"]
                best_component = {
                    "name": component,
                    "score": data["score"],
                    "weighted_score": data["weighted_score"]
                }
        
        return best_component
    
    @staticmethod
    def _get_worst_component(score_breakdown):
        """Get the component that needs the most improvement."""
        if not score_breakdown:
            return None
        
        min_score = float('inf')
        worst_component = None
        
        for component, data in score_breakdown.items():
            if data["weighted_score"] < min_score:
                min_score = data["weighted_score"]
                worst_component = {
                    "name": component,
                    "score": data["score"],
                    "weighted_score": data["weighted_score"]
                }
        
        return worst_component