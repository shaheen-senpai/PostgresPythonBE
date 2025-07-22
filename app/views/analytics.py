"""
Analytics API endpoints for chart data generation.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers.analytics_controller import analytics_controller
from app.middlewares.rbac import (
    get_current_active_user,
    get_current_superuser
)
from app.models.user import User

router = APIRouter()


# Employee Analytics Endpoints

@router.get("/employee/mood-weekly", response_model=Dict[str, Any])
def get_employee_mood_weekly(
    weeks: int = Query(4, ge=1, le=12, description="Number of weeks to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get employee's mood distribution per week for bar chart.
    
    Employee access: ✅ Own data only
    Admin access: ✅ Own data only (when using this endpoint)
    """
    return analytics_controller.get_mood_bar_chart_weekly(
        db=db,
        user_id=current_user.id,
        weeks=weeks
    )


@router.get("/employee/energy-heatmap", response_model=Dict[str, Any])
def get_employee_energy_heatmap(
    year: Optional[int] = Query(None, description="Year (default: current year)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month (default: current month)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get employee's energy level heatmap like GitHub contributions.
    
    Employee access: ✅ Own data only
    Admin access: ✅ Own data only (when using this endpoint)
    """
    return analytics_controller.get_energy_heatmap_monthly(
        db=db,
        user_id=current_user.id,
        year=year,
        month=month
    )


@router.get("/employee/complexity-satisfaction", response_model=Dict[str, Any])
def get_employee_complexity_satisfaction(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get employee's complexity vs satisfaction chart data.
    
    Employee access: ✅ Own data only
    Admin access: ✅ Own data only (when using this endpoint)
    """
    return analytics_controller.get_complexity_vs_satisfaction(
        db=db,
        user_id=current_user.id,
        days=days
    )


@router.get("/employee/energy-satisfaction", response_model=Dict[str, Any])
def get_employee_energy_satisfaction(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get employee's energy vs satisfaction scatter plot data.
    
    Employee access: ✅ Own data only
    Admin access: ✅ Own data only (when using this endpoint)
    """
    return analytics_controller.get_energy_vs_satisfaction(
        db=db,
        user_id=current_user.id,
        days=days
    )


# Admin Analytics Endpoints

@router.get("/admin/mood-distribution", response_model=Dict[str, Any])
def get_admin_mood_distribution(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get mood distribution of all employees for pie chart.
    
    Employee access: ❌ Forbidden
    Admin access: ✅ All employees' data
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return analytics_controller.get_mood_distribution_pie(
        db=db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/admin/energy-trend", response_model=Dict[str, Any])
def get_admin_energy_trend(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get overall energy level trend line chart for all employees.
    
    Employee access: ❌ Forbidden
    Admin access: ✅ All employees' data
    """
    return analytics_controller.get_overall_energy_line_chart(
        db=db,
        days=days
    )


@router.get("/admin/complexity-count", response_model=Dict[str, Any])
def get_admin_complexity_count(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get task complexity count for all employees bar chart.
    
    Employee access: ❌ Forbidden
    Admin access: ✅ All employees' data
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return analytics_controller.get_complexity_count_bar(
        db=db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/admin/satisfaction-weekly", response_model=Dict[str, Any])
def get_admin_satisfaction_weekly(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get satisfaction levels for past week (Mon-Sun) for all employees.
    
    Employee access: ❌ Forbidden
    Admin access: ✅ All employees' data
    """
    return analytics_controller.get_satisfaction_weekly_bar(db=db)


# Additional Analytics Endpoints

@router.get("/employee/dashboard-summary", response_model=Dict[str, Any])
def get_employee_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get employee dashboard summary with key metrics.
    
    Employee access: ✅ Own data only
    Admin access: ✅ Own data only (when using this endpoint)
    """
    # Get data for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    from app.models.vibe_log import VibeLog
    from sqlalchemy import and_, func
    
    # Get basic stats
    logs = db.query(VibeLog).filter(
        and_(
            VibeLog.user_id == current_user.id,
            VibeLog.created_at >= start_date,
            VibeLog.created_at <= end_date,
            VibeLog.deleted_at.is_(None)
        )
    ).all()
    
    if not logs:
        return {
            "total_entries": 0,
            "avg_energy": 0,
            "avg_satisfaction": 0,
            "most_common_mood": "N/A",
            "most_common_complexity": "N/A"
        }
    
    from collections import Counter
    
    total_entries = len(logs)
    avg_energy = sum(log.energy_level for log in logs) / total_entries
    avg_satisfaction = sum(log.satisfaction for log in logs) / total_entries
    
    mood_counter = Counter(log.mood.value for log in logs)
    complexity_counter = Counter(log.complexity.value for log in logs)
    
    return {
        "total_entries": total_entries,
        "avg_energy": round(avg_energy, 1),
        "avg_satisfaction": round(avg_satisfaction, 1),
        "most_common_mood": mood_counter.most_common(1)[0][0] if mood_counter else "N/A",
        "most_common_complexity": complexity_counter.most_common(1)[0][0] if complexity_counter else "N/A",
        "period": "Last 30 days"
    }


@router.get("/admin/dashboard-summary", response_model=Dict[str, Any])
def get_admin_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get admin dashboard summary with organization-wide metrics.
    
    Employee access: ❌ Forbidden
    Admin access: ✅ All employees' data
    """
    # Get data for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    from app.models.vibe_log import VibeLog
    from app.models.user import User as UserModel
    from sqlalchemy import and_, func, distinct
    
    # Get organization stats
    total_logs = db.query(VibeLog).filter(
        and_(
            VibeLog.created_at >= start_date,
            VibeLog.created_at <= end_date,
            VibeLog.deleted_at.is_(None)
        )
    ).count()
    
    active_users = db.query(distinct(VibeLog.user_id)).filter(
        and_(
            VibeLog.created_at >= start_date,
            VibeLog.created_at <= end_date,
            VibeLog.deleted_at.is_(None)
        )
    ).count()
    
    total_users = db.query(UserModel).filter(
        UserModel.deleted_at.is_(None)
    ).count()
    
    # Get average metrics
    avg_metrics = db.query(
        func.avg(VibeLog.energy_level).label('avg_energy'),
        func.avg(VibeLog.satisfaction).label('avg_satisfaction')
    ).filter(
        and_(
            VibeLog.created_at >= start_date,
            VibeLog.created_at <= end_date,
            VibeLog.deleted_at.is_(None)
        )
    ).first()
    
    return {
        "total_logs": total_logs,
        "active_users": active_users,
        "total_users": total_users,
        "engagement_rate": round((active_users / total_users * 100), 1) if total_users > 0 else 0,
        "avg_energy": round(float(avg_metrics.avg_energy), 1) if avg_metrics.avg_energy else 0,
        "avg_satisfaction": round(float(avg_metrics.avg_satisfaction), 1) if avg_metrics.avg_satisfaction else 0,
        "period": "Last 30 days"
    }
