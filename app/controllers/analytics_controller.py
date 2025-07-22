"""
Analytics controller for generating chart data from vibe logs.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from collections import defaultdict, Counter

from app.models.vibe_log import VibeLog, MoodEnum, ComplexityEnum
class AnalyticsController:
    """Controller for analytics and chart data generation."""

    # Employee Analytics Methods
    
    def get_mood_bar_chart_weekly(
        self, 
        db: Session, 
        user_id: int, 
        weeks: int = 4
    ) -> Dict[str, Any]:
        """
        Get mood distribution per week for bar chart.
        
        Args:
            db: Database session
            user_id: User ID
            weeks: Number of weeks to look back (default: 4)
            
        Returns:
            Dict with weeks as keys and mood counts as values
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks)
        
        # Query vibe logs for the period
        logs = db.query(VibeLog).filter(
            and_(
                VibeLog.user_id == user_id,
                VibeLog.created_at >= start_date,
                VibeLog.created_at <= end_date,
                VibeLog.deleted_at.is_(None)
            )
        ).all()
        
        # Group by week and mood
        weekly_data = defaultdict(lambda: defaultdict(int))
        
        for log in logs:
            # Calculate week number
            week_start = log.created_at - timedelta(days=log.created_at.weekday())
            week_key = week_start.strftime("%Y-W%U")
            week_label = f"{week_start.strftime('%b %d')} - {(week_start + timedelta(days=6)).strftime('%b %d')}"
            
            weekly_data[week_label][log.mood.value] += 1
        
        # Format for chart
        chart_data = {
            "labels": list(weekly_data.keys()),
            "datasets": []
        }
        
        # Create dataset for each mood
        moods = [mood.value for mood in MoodEnum]
        colors = {
            "sad": "#FF6B6B",
            "angry": "#FF4757", 
            "happy": "#2ED573",
            "good": "#5352ED",
            "excited": "#FFA502"
        }
        
        for mood in moods:
            chart_data["datasets"].append({
                "label": mood.title(),
                "data": [weekly_data[week][mood] for week in chart_data["labels"]],
                "backgroundColor": colors.get(mood, "#95A5A6")
            })
        
        return chart_data

    def get_energy_heatmap_monthly(
        self, 
        db: Session, 
        user_id: int, 
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get energy level heatmap data like GitHub contributions.
        
        Args:
            db: Database session
            user_id: User ID
            year: Year (default: current year)
            month: Month (default: current month)
            
        Returns:
            Dict with date and energy level data
        """
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
            
        # Get first and last day of month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Query energy levels for the month
        logs = db.query(VibeLog).filter(
            and_(
                VibeLog.user_id == user_id,
                VibeLog.created_at >= start_date,
                VibeLog.created_at <= end_date,
                VibeLog.deleted_at.is_(None)
            )
        ).all()
        
        # Group by date and calculate average energy
        daily_energy = defaultdict(list)
        for log in logs:
            date_key = log.created_at.strftime("%Y-%m-%d")
            daily_energy[date_key].append(log.energy_level)
        
        # Calculate averages and format for heatmap
        heatmap_data = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            energy_values = daily_energy.get(date_str, [])
            avg_energy = sum(energy_values) / len(energy_values) if energy_values else 0
            
            heatmap_data.append({
                "date": date_str,
                "energy": round(avg_energy, 1),
                "count": len(energy_values)
            })
            
            current_date += timedelta(days=1)
        
        return {
            "data": heatmap_data,
            "month": f"{start_date.strftime('%B %Y')}",
            "max_energy": 5,  # Energy scale is 1-5
            "min_energy": 1
        }

    def get_complexity_vs_satisfaction(
        self, 
        db: Session, 
        user_id: int, 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get complexity vs satisfaction scatter plot data.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Dict with scatter plot data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logs = db.query(VibeLog).filter(
            and_(
                VibeLog.user_id == user_id,
                VibeLog.created_at >= start_date,
                VibeLog.created_at <= end_date,
                VibeLog.deleted_at.is_(None)
            )
        ).all()
        
        # Group by complexity and calculate average satisfaction
        complexity_satisfaction = defaultdict(list)
        for log in logs:
            complexity_satisfaction[log.complexity.value].append(log.satisfaction)
        
        # Calculate averages
        chart_data = {
            "labels": [complexity.value for complexity in ComplexityEnum],
            "datasets": [{
                "label": "Average Satisfaction",
                "data": [],
                "backgroundColor": "#3498DB"
            }]
        }
        
        for complexity in ComplexityEnum:
            satisfactions = complexity_satisfaction.get(complexity.value, [])
            avg_satisfaction = sum(satisfactions) / len(satisfactions) if satisfactions else 0
            chart_data["datasets"][0]["data"].append(round(avg_satisfaction, 1))
        
        return chart_data

    def get_energy_vs_satisfaction(
        self, 
        db: Session, 
        user_id: int, 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get energy vs satisfaction correlation data.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Dict with scatter plot data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logs = db.query(VibeLog).filter(
            and_(
                VibeLog.user_id == user_id,
                VibeLog.created_at >= start_date,
                VibeLog.created_at <= end_date,
                VibeLog.deleted_at.is_(None)
            )
        ).all()
        
        # Create scatter plot data
        scatter_data = []
        for log in logs:
            scatter_data.append({
                "x": log.energy_level,
                "y": log.satisfaction,
                "date": log.created_at.strftime("%Y-%m-%d")
            })
        
        return {
            "data": scatter_data,
            "x_label": "Energy Level (1-5)",
            "y_label": "Satisfaction (0-10)",
            "title": f"Energy vs Satisfaction ({days} days)"
        }

    # Admin Analytics Methods
    
    def get_mood_distribution_pie(
        self, 
        db: Session, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get mood distribution of all employees for pie chart.
        
        Args:
            db: Database session
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dict with pie chart data
        """
        logs = db.query(VibeLog).filter(
            and_(
                VibeLog.created_at >= start_date,
                VibeLog.created_at <= end_date,
                VibeLog.deleted_at.is_(None)
            )
        ).all()
        
        # Count moods
        mood_counts = Counter(log.mood.value for log in logs)
        
        colors = {
            "sad": "#FF6B6B",
            "angry": "#FF4757", 
            "happy": "#2ED573",
            "good": "#5352ED",
            "excited": "#FFA502"
        }
        
        return {
            "labels": list(mood_counts.keys()),
            "data": list(mood_counts.values()),
            "backgroundColor": [colors.get(mood, "#95A5A6") for mood in mood_counts.keys()],
            "total_entries": sum(mood_counts.values())
        }

    def get_overall_energy_line_chart(
        self, 
        db: Session, 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get overall energy level trend for line chart.
        
        Args:
            db: Database session
            days: Number of days to analyze
            
        Returns:
            Dict with line chart data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query daily average energy levels
        daily_avg = db.query(
            func.date(VibeLog.created_at).label('date'),
            func.avg(VibeLog.energy_level).label('avg_energy')
        ).filter(
            and_(
                VibeLog.created_at >= start_date,
                VibeLog.created_at <= end_date,
                VibeLog.deleted_at.is_(None)
            )
        ).group_by(func.date(VibeLog.created_at)).all()
        
        # Format for line chart
        dates = []
        energy_values = []
        
        for result in daily_avg:
            dates.append(result.date.strftime("%Y-%m-%d"))
            energy_values.append(round(float(result.avg_energy), 2))
        
        return {
            "labels": dates,
            "datasets": [{
                "label": "Average Energy Level",
                "data": energy_values,
                "borderColor": "#3498DB",
                "backgroundColor": "rgba(52, 152, 219, 0.1)",
                "tension": 0.4
            }]
        }

    def get_complexity_count_bar(
        self, 
        db: Session, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get task complexity count for bar chart.
        
        Args:
            db: Database session
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dict with bar chart data
        """
        logs = db.query(VibeLog).filter(
            and_(
                VibeLog.created_at >= start_date,
                VibeLog.created_at <= end_date,
                VibeLog.deleted_at.is_(None)
            )
        ).all()
        
        # Count complexity levels
        complexity_counts = Counter(log.complexity.value for log in logs)
        
        # Ensure all complexity levels are represented
        all_complexities = [complexity.value for complexity in ComplexityEnum]
        
        return {
            "labels": all_complexities,
            "datasets": [{
                "label": "Task Count",
                "data": [complexity_counts.get(complexity, 0) for complexity in all_complexities],
                "backgroundColor": ["#E74C3C", "#F39C12", "#F1C40F", "#8E44AD"]
            }]
        }

    def get_satisfaction_weekly_bar(
        self, 
        db: Session
    ) -> Dict[str, Any]:
        """
        Get satisfaction levels for past week (Mon-Sun) bar chart.
        
        Args:
            db: Database session
            
        Returns:
            Dict with weekly satisfaction bar chart data
        """
        # Get last Monday as start of week
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday)
        week_start = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        
        logs = db.query(VibeLog).filter(
            and_(
                VibeLog.created_at >= week_start,
                VibeLog.created_at < week_end,
                VibeLog.deleted_at.is_(None)
            )
        ).all()
        
        # Group by day of week
        daily_satisfaction = defaultdict(list)
        for log in logs:
            day_name = log.created_at.strftime("%A")
            daily_satisfaction[day_name].append(log.satisfaction)
        
        # Calculate averages for each day
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        satisfaction_data = []
        
        for day in days_of_week:
            satisfactions = daily_satisfaction.get(day, [])
            avg_satisfaction = sum(satisfactions) / len(satisfactions) if satisfactions else 0
            satisfaction_data.append(round(avg_satisfaction, 1))
        
        return {
            "labels": days_of_week,
            "datasets": [{
                "label": "Average Satisfaction",
                "data": satisfaction_data,
                "backgroundColor": "#2ECC71"
            }],
            "week_range": f"{week_start.strftime('%b %d')} - {(week_end - timedelta(days=1)).strftime('%b %d, %Y')}"
        }


# Create controller instance
analytics_controller = AnalyticsController()
