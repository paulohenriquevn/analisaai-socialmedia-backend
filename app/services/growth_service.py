"""
Service for calculating and processing growth metrics for influencers.
"""
import logging
from datetime import datetime, date, timedelta
import numpy as np
from app.extensions import db
from app.models.influencer import Influencer
from app.models.growth import InfluencerGrowth

logger = logging.getLogger(__name__)

class GrowthService:
    """Service for calculating and tracking growth metrics."""
    
    @staticmethod
    def calculate_growth_metrics(influencer_id):
        """
        Calculate growth metrics for a specific influencer.
        
        Args:
            influencer_id: ID of the influencer to calculate metrics for
            
        Returns:
            dict: The calculated growth metrics or None if error
        """
        try:
            logger.info(f"Calculating growth metrics for influencer ID: {influencer_id}")
            
            # Get the influencer
            influencer = Influencer.query.get(influencer_id)
            if not influencer:
                logger.error(f"Influencer with ID {influencer_id} not found")
                return None
            
            # Current and past metrics
            current_date = date.today()
            current_followers = influencer.followers_count
            
            # Get historical metrics to calculate growth
            growth_metrics = GrowthService.get_historical_metrics(influencer_id, current_date)
            
            # Calculate new followers
            new_followers_daily = 0
            new_followers_weekly = 0
            new_followers_monthly = 0
            
            # Calculate growth rates
            daily_growth_rate = 0.0
            weekly_growth_rate = 0.0
            monthly_growth_rate = 0.0
            
            # Retention and churn rates
            retention_rate = 100.0  # Default to 100% retention if we can't calculate
            churn_rate = 0.0       # Default to 0% churn if we can't calculate
            
            # If we have previous data, calculate growth and retention
            if growth_metrics:
                # Most recent metrics (for daily growth)
                yesterday_metrics = next((m for m in growth_metrics if m.date == current_date - timedelta(days=1)), None)
                if yesterday_metrics and yesterday_metrics.followers_count > 0:
                    new_followers_daily = current_followers - yesterday_metrics.followers_count
                    daily_growth_rate = (current_followers - yesterday_metrics.followers_count) / yesterday_metrics.followers_count * 100
                
                # Weekly growth
                week_ago_metrics = next((m for m in growth_metrics if m.date == current_date - timedelta(days=7)), None)
                if week_ago_metrics and week_ago_metrics.followers_count > 0:
                    new_followers_weekly = current_followers - week_ago_metrics.followers_count
                    weekly_growth_rate = (current_followers - week_ago_metrics.followers_count) / week_ago_metrics.followers_count * 100
                
                # Monthly growth
                month_ago_metrics = next((m for m in growth_metrics if m.date == current_date - timedelta(days=30)), None)
                if month_ago_metrics and month_ago_metrics.followers_count > 0:
                    new_followers_monthly = current_followers - month_ago_metrics.followers_count
                    monthly_growth_rate = (current_followers - month_ago_metrics.followers_count) / month_ago_metrics.followers_count * 100
                
                # Calculate retention and churn rates (based on historical data)
                # We'll use a simplified approach that estimates retention from net growth and estimated unfollows
                if yesterday_metrics and yesterday_metrics.followers_count > 0:
                    # Estimate the churn rate using industry averages if we don't have actual data
                    # Typical social media churn rates range from 5-10% monthly, so we'll use ~0.2-0.3% daily
                    estimated_daily_churn = 0.25  # 0.25% daily churn
                    estimated_unfollows = int(yesterday_metrics.followers_count * estimated_daily_churn / 100)
                    
                    # Gross new followers = net new followers + estimated unfollows
                    gross_new_followers = new_followers_daily + estimated_unfollows
                    
                    # Retention rate = 1 - (estimated_unfollows / yesterday's followers)
                    retention_rate = 100 - estimated_daily_churn
                    churn_rate = estimated_daily_churn
            
            # Calculate growth velocity and acceleration
            growth_velocity = GrowthService.calculate_growth_velocity(influencer_id, current_date)
            growth_acceleration = GrowthService.calculate_growth_acceleration(influencer_id, current_date)
            
            # Calculate projections
            projected_followers_30d = GrowthService.project_followers(current_followers, daily_growth_rate, 30)
            projected_followers_90d = GrowthService.project_followers(current_followers, daily_growth_rate, 90)
            
            # Create metrics data
            metrics = {
                'influencer_id': influencer_id,
                'date': current_date,
                'followers_count': current_followers,
                'new_followers_daily': new_followers_daily,
                'new_followers_weekly': new_followers_weekly,
                'new_followers_monthly': new_followers_monthly,
                'retention_rate': retention_rate,
                'churn_rate': churn_rate,
                'daily_growth_rate': daily_growth_rate,
                'weekly_growth_rate': weekly_growth_rate,
                'monthly_growth_rate': monthly_growth_rate,
                'growth_velocity': growth_velocity,
                'growth_acceleration': growth_acceleration,
                'projected_followers_30d': projected_followers_30d,
                'projected_followers_90d': projected_followers_90d
            }
            
            # Save the metrics
            result = GrowthService.save_growth_metrics(metrics)
            if result:
                logger.info(f"Successfully saved growth metrics for influencer {influencer_id}")
                return metrics
            else:
                logger.error(f"Failed to save growth metrics for influencer {influencer_id}")
                return None
            
        except Exception as e:
            logger.error(f"Error calculating growth metrics for influencer {influencer_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def get_historical_metrics(influencer_id, end_date=None, days=30):
        """
        Get historical growth metrics for an influencer.
        
        Args:
            influencer_id: ID of the influencer
            end_date: End date for data retrieval (defaults to today)
            days: Number of days of history to retrieve
            
        Returns:
            list: Historical growth metrics 
        """
        if end_date is None:
            end_date = date.today()
            
        start_date = end_date - timedelta(days=days)
        
        # Get stored growth metrics
        growth_metrics = InfluencerGrowth.query.filter(
            InfluencerGrowth.influencer_id == influencer_id,
            InfluencerGrowth.date >= start_date,
            InfluencerGrowth.date <= end_date
        ).order_by(InfluencerGrowth.date.desc()).all()
        
        return growth_metrics
    
    @staticmethod
    def calculate_growth_velocity(influencer_id, current_date=None, days=7):
        """
        Calculate growth velocity (average daily follower growth) over a period.
        
        Args:
            influencer_id: ID of the influencer
            current_date: Current date (defaults to today)
            days: Number of days to analyze
            
        Returns:
            float: Average daily follower growth
        """
        if current_date is None:
            current_date = date.today()
            
        start_date = current_date - timedelta(days=days)
        
        # Get start and end metrics
        start_metrics = InfluencerGrowth.query.filter(
            InfluencerGrowth.influencer_id == influencer_id,
            InfluencerGrowth.date == start_date
        ).first()
        
        end_metrics = InfluencerGrowth.query.filter(
            InfluencerGrowth.influencer_id == influencer_id,
            InfluencerGrowth.date == current_date
        ).first()
        
        # If we don't have both metrics, try using the influencer's current count
        # and the oldest available metric in the range
        if not start_metrics or not end_metrics:
            # Get the influencer
            influencer = Influencer.query.get(influencer_id)
            if not influencer:
                return 0.0
                
            end_followers = influencer.followers_count
            
            # Find the oldest available metric in our date range
            oldest_metric = InfluencerGrowth.query.filter(
                InfluencerGrowth.influencer_id == influencer_id,
                InfluencerGrowth.date >= start_date,
                InfluencerGrowth.date <= current_date
            ).order_by(InfluencerGrowth.date.asc()).first()
            
            if oldest_metric:
                start_followers = oldest_metric.followers_count
                elapsed_days = (current_date - oldest_metric.date).days
                if elapsed_days > 0:
                    return (end_followers - start_followers) / elapsed_days
            
            # If we have absolutely no data, return 0
            return 0.0
            
        # Calculate velocity from start to end
        start_followers = start_metrics.followers_count
        end_followers = end_metrics.followers_count
        
        if days > 0:
            velocity = (end_followers - start_followers) / days
            return velocity
            
        return 0.0
    
    @staticmethod
    def calculate_growth_acceleration(influencer_id, current_date=None):
        """
        Calculate growth acceleration (change in velocity) over time.
        
        Args:
            influencer_id: ID of the influencer
            current_date: Current date (defaults to today)
            
        Returns:
            float: Growth acceleration (change in daily growth rate)
        """
        if current_date is None:
            current_date = date.today()
            
        # Calculate current velocity (last 7 days)
        current_velocity = GrowthService.calculate_growth_velocity(
            influencer_id, current_date, days=7
        )
        
        # Calculate previous velocity (7 days before that)
        previous_period_end = current_date - timedelta(days=7)
        previous_velocity = GrowthService.calculate_growth_velocity(
            influencer_id, previous_period_end, days=7
        )
        
        # Calculate acceleration (change in velocity)
        acceleration = current_velocity - previous_velocity
        
        return acceleration
    
    @staticmethod
    def project_followers(current_followers, daily_growth_rate, days):
        """
        Project future follower count based on current growth rate.
        
        Args:
            current_followers: Current follower count
            daily_growth_rate: Daily growth rate as a percentage
            days: Number of days into the future to project
            
        Returns:
            int: Projected follower count
        """
        # Convert daily growth rate from percentage to multiplier
        daily_multiplier = 1 + (daily_growth_rate / 100)
        
        # Apply compound growth for the number of days
        projected_followers = current_followers * (daily_multiplier ** days)
        
        return int(projected_followers)
    
    @staticmethod
    def save_growth_metrics(metrics_data):
        """
        Save growth metrics to the database.
        
        Args:
            metrics_data: Dict containing growth metrics
            
        Returns:
            InfluencerGrowth: Saved growth metrics record or None if error
        """
        try:
            # Check if metrics for this influencer and date already exist
            existing = InfluencerGrowth.query.filter_by(
                influencer_id=metrics_data['influencer_id'],
                date=metrics_data['date']
            ).first()
            
            if existing:
                # Update existing metrics
                for key, value in metrics_data.items():
                    if key != 'influencer_id' and key != 'date' and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                growth_record = existing
            else:
                # Create new metrics record
                growth_record = InfluencerGrowth(**metrics_data)
                db.session.add(growth_record)
            
            db.session.commit()
            return growth_record
            
        except Exception as e:
            logger.error(f"Error saving growth metrics: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_growth_metrics(influencer_id, start_date=None, end_date=None):
        """
        Get growth metrics for an influencer within a date range.
        
        Args:
            influencer_id: ID of the influencer
            start_date: Start date for metrics (optional)
            end_date: End date for metrics (optional)
            
        Returns:
            list: List of growth metrics or empty list if none found
        """
        query = InfluencerGrowth.query.filter_by(influencer_id=influencer_id)
        
        if start_date:
            query = query.filter(InfluencerGrowth.date >= start_date)
        
        if end_date:
            query = query.filter(InfluencerGrowth.date <= end_date)
        
        # Order by date (most recent first)
        query = query.order_by(InfluencerGrowth.date.desc())
        
        return query.all()
    
    @staticmethod
    def calculate_all_influencers_growth():
        """
        Calculate growth metrics for all influencers.
        
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
                metrics = GrowthService.calculate_growth_metrics(influencer.id)
                if metrics:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception:
                results['failed'] += 1
        
        return results