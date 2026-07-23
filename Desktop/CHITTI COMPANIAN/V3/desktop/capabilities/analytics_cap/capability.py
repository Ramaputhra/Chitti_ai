"""
Personal Analytics Capability

Provides tools for time tracking, habit insights, productivity metrics,
and personal analytics dashboards.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import os

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import IProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.health import ProviderHealth


class TaskCategory(str, Enum):
    """Task categories for tracking."""
    DEVELOPMENT = "development"
    MEETING = "meeting"
    COMMUNICATION = "communication"
    LEARNING = "learning"
    ADMIN = "administration"
    BREAK = "break"
    OTHER = "other"


class ProductivityLevel(str, Enum):
    """Productivity levels."""
    EXCELLENT = "excellent"    # 8-10
    GOOD = "good"             # 6-8
    AVERAGE = "average"        # 4-6
    LOW = "low"                # 2-4
    POOR = "poor"             # 0-2


@dataclass
class TimeEntry:
    """A time tracking entry."""
    id: str
    task_name: str
    category: TaskCategory
    start_time: str
    end_time: Optional[str]
    duration_minutes: int
    notes: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class HabitRecord:
    """A habit tracking record."""
    id: str
    habit_name: str
    created_at: str
    completions: int
    streak: int
    last_completed: Optional[str]
    frequency: str  # daily, weekly
    target_per_week: int


@dataclass
class ProductivitySnapshot:
    """A productivity snapshot."""
    date: str
    total_focus_minutes: int
    tasks_completed: int
    meetings_minutes: int
    productive_hours: float
    breaks_taken: int
    score: float


class PersonalAnalyticsCapability:
    """
    Personal Analytics capability for CHITTI.
    
    Tools:
    - start_time_tracking: Start tracking time for a task
    - stop_time_tracking: Stop current time tracking
    - get_time_summary: Get today's time summary
    - get_weekly_report: Get weekly productivity report
    - get_monthly_report: Get monthly analytics
    - track_habit: Record habit completion
    - get_habit_streak: Get habit streak info
    - get_productivity_score: Calculate productivity score
    - get_peak_hours: Find most productive hours
    - get_goal_progress: Track goal progress
    - get_daily_summary: Get daily summary
    - categorize_time: Categorize time entries
    """
    
    def __init__(self, logger: Optional[ILoggingService] = None):
        self.logger = logger or MockLogger()
        self._state = ServiceState.STOPPED
        self._is_healthy = True
        
        # Data storage
        self._time_entries: List[TimeEntry] = []
        self._habits: List[HabitRecord] = []
        self._current_tracking: Optional[TimeEntry] = None
        self._goals: Dict[str, Dict] = {}
        
        # Analytics cache
        self._daily_summaries: Dict[str, ProductivitySnapshot] = {}
        
        self.logger.info("[PersonalAnalytics] Initialized")
    
    @property
    def name(self) -> str:
        return "PersonalAnalyticsCapability"
    
    @property
    def state(self) -> ServiceState:
        return self._state
    
    def initialize(self) -> None:
        """Initialize the capability."""
        self._state = ServiceState.RUNNING
        self._is_healthy = True
        self.logger.info("[PersonalAnalytics] Started")
    
    def shutdown(self) -> None:
        """Shutdown the capability."""
        # Auto-stop any tracking
        if self._current_tracking:
            self.stop_time_tracking()
        self._state = ServiceState.STOPPED
        self.logger.info("[PersonalAnalytics] Stopped")
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy" if self._is_healthy else "unhealthy",
            "tracking_active": self._current_tracking is not None,
            "total_entries": len(self._time_entries),
            "total_habits": len(self._habits)
        }
    
    def discover_tools(self) -> List[str]:
        """Return list of available tools."""
        return [
            "start_time_tracking",
            "stop_time_tracking",
            "get_current_tracking",
            "get_time_summary",
            "get_weekly_report",
            "get_monthly_report",
            "track_habit",
            "get_habit_streak",
            "get_all_habits",
            "create_habit",
            "delete_habit",
            "get_productivity_score",
            "get_peak_hours",
            "get_goal_progress",
            "set_goal",
            "get_daily_summary",
            "categorize_time",
            "get_category_breakdown",
            "get_focus_breakdown"
        ]
    
    # ========== TIME TRACKING TOOLS ==========
    
    def start_time_tracking(
        self,
        task_name: str,
        category: str = "other",
        notes: str = "",
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Start tracking time for a task.
        
        Args:
            task_name: Name of the task
            category: Task category
            notes: Optional notes
            tags: Optional tags
            
        Returns:
            Tracking info
        """
        # Stop any existing tracking
        if self._current_tracking:
            self.stop_time_tracking()
        
        entry_id = f"time_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        try:
            cat = TaskCategory(category.lower())
        except ValueError:
            cat = TaskCategory.OTHER
        
        entry = TimeEntry(
            id=entry_id,
            task_name=task_name,
            category=cat,
            start_time=datetime.now().isoformat(),
            end_time=None,
            duration_minutes=0,
            notes=notes,
            tags=tags or []
        )
        
        self._current_tracking = entry
        self.logger.info(f"[PersonalAnalytics] Started tracking: {task_name}")
        
        return {
            "id": entry_id,
            "task_name": task_name,
            "category": cat.value,
            "started_at": entry.start_time,
            "status": "tracking"
        }
    
    def stop_time_tracking(self) -> Dict[str, Any]:
        """
        Stop current time tracking.
        
        Returns:
            Summary of tracked time
        """
        if not self._current_tracking:
            return {"error": "No active time tracking"}
        
        entry = self._current_tracking
        entry.end_time = datetime.now().isoformat()
        
        start = datetime.fromisoformat(entry.start_time)
        end = datetime.fromisoformat(entry.end_time)
        entry.duration_minutes = int((end - start).total_seconds() / 60)
        
        self._time_entries.append(entry)
        self._current_tracking = None
        
        self.logger.info(f"[PersonalAnalytics] Stopped tracking: {entry.task_name} ({entry.duration_minutes}min)")
        
        return {
            "id": entry.id,
            "task_name": entry.task_name,
            "category": entry.category.value,
            "duration_minutes": entry.duration_minutes,
            "start_time": entry.start_time,
            "end_time": entry.end_time,
            "notes": entry.notes,
            "tags": entry.tags
        }
    
    def get_current_tracking(self) -> Dict[str, Any]:
        """
        Get current tracking status.
        
        Returns:
            Current tracking info
        """
        if not self._current_tracking:
            return {"tracking": False}
        
        entry = self._current_tracking
        start = datetime.fromisoformat(entry.start_time)
        elapsed = int((datetime.now() - start).total_seconds() / 60)
        
        return {
            "tracking": True,
            "id": entry.id,
            "task_name": entry.task_name,
            "category": entry.category.value,
            "started_at": entry.start_time,
            "elapsed_minutes": elapsed
        }
    
    # ========== TIME SUMMARY TOOLS ==========
    
    def get_time_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get today's time summary.
        
        Args:
            date: Optional date (YYYY-MM-DD)
            
        Returns:
            Time summary by category
        """
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        
        # Filter entries for target date
        day_entries = [
            e for e in self._time_entries
            if e.start_time.startswith(target_date)
        ]
        
        # Include current tracking
        if self._current_tracking and self._current_tracking.start_time.startswith(target_date):
            elapsed = int((datetime.now() - datetime.fromisoformat(self._current_tracking.start_time)).total_seconds() / 60)
            day_entries.append(TimeEntry(
                id="current",
                task_name=self._current_tracking.task_name,
                category=self._current_tracking.category,
                start_time=self._current_tracking.start_time,
                end_time=None,
                duration_minutes=elapsed
            ))
        
        # Aggregate by category
        category_totals: Dict[str, int] = {}
        for entry in day_entries:
            cat = entry.category.value
            if cat not in category_totals:
                category_totals[cat] = 0
            category_totals[cat] += entry.duration_minutes
        
        total_minutes = sum(category_totals.values())
        
        return {
            "date": target_date,
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 2),
            "by_category": {
                cat: {
                    "minutes": mins,
                    "hours": round(mins / 60, 2),
                    "percentage": round(mins / total_minutes * 100, 1) if total_minutes > 0 else 0
                }
                for cat, mins in category_totals.items()
            },
            "entries": len(day_entries)
        }
    
    def get_weekly_report(self) -> Dict[str, Any]:
        """
        Get weekly productivity report.
        
        Returns:
            Weekly analytics
        """
        today = datetime.now()
        week_data = []
        
        for i in range(7):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            summary = self.get_time_summary(date)
            week_data.append({
                "date": date,
                "day_name": (today - timedelta(days=i)).strftime("%A"),
                "total_hours": summary["total_hours"],
                "focus_hours": summary["by_category"].get("development", {}).get("hours", 0)
            })
        
        total_focus = sum(d["focus_hours"] for d in week_data)
        avg_focus = total_focus / 7
        
        # Find best and worst days
        best_day = max(week_data, key=lambda d: d["focus_hours"])
        worst_day = min(week_data, key=lambda d: d["focus_hours"])
        
        return {
            "week_start": (today - timedelta(days=6)).strftime("%Y-%m-%d"),
            "week_end": today.strftime("%Y-%m-%d"),
            "days": week_data,
            "total_focus_hours": round(total_focus, 2),
            "daily_average": round(avg_focus, 2),
            "best_day": {"date": best_day["date"], "hours": best_day["focus_hours"]},
            "worst_day": {"date": worst_day["date"], "hours": worst_day["focus_hours"]},
            "goal_hours_per_day": 4,
            "goal_met_days": sum(1 for d in week_data if d["focus_hours"] >= 4)
        }
    
    def get_monthly_report(self) -> Dict[str, Any]:
        """
        Get monthly analytics.
        
        Returns:
            Monthly analytics
        """
        today = datetime.now()
        month_start = today.replace(day=1)
        
        # Get all entries for this month
        month_entries = [
            e for e in self._time_entries
            if datetime.fromisoformat(e.start_time) >= month_start
        ]
        
        # Calculate totals
        total_minutes = sum(e.duration_minutes for e in month_entries)
        
        # Category breakdown
        category_totals: Dict[str, int] = {}
        for entry in month_entries:
            cat = entry.category.value
            if cat not in category_totals:
                category_totals[cat] = 0
            category_totals[cat] += entry.duration_minutes
        
        # Calculate streaks
        days_with_work = len(set(
            e.start_time[:10] for e in month_entries
        ))
        
        return {
            "month": today.strftime("%B %Y"),
            "total_hours": round(total_minutes / 60, 2),
            "total_tasks": len(month_entries),
            "days_with_work": days_with_work,
            "by_category": {
                cat: {
                    "hours": round(mins / 60, 2),
                    "percentage": round(mins / total_minutes * 100, 1) if total_minutes > 0 else 0
                }
                for cat, mins in category_totals.items()
            },
            "daily_average_hours": round((total_minutes / 60) / today.day, 2) if today.day > 0 else 0
        }
    
    # ========== HABIT TRACKING TOOLS ==========
    
    def create_habit(
        self,
        habit_name: str,
        frequency: str = "daily",
        target_per_week: int = 7
    ) -> Dict[str, Any]:
        """
        Create a new habit to track.
        
        Args:
            habit_name: Name of the habit
            frequency: daily or weekly
            target_per_week: Target completions per week
            
        Returns:
            Created habit info
        """
        habit_id = f"habit_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        habit = HabitRecord(
            id=habit_id,
            habit_name=habit_name,
            created_at=datetime.now().isoformat(),
            completions=0,
            streak=0,
            last_completed=None,
            frequency=frequency,
            target_per_week=target_per_week
        )
        
        self._habits.append(habit)
        self.logger.info(f"[PersonalAnalytics] Created habit: {habit_name}")
        
        return {
            "id": habit_id,
            "name": habit_name,
            "frequency": frequency,
            "target_per_week": target_per_week,
            "streak": 0,
            "completions": 0
        }
    
    def track_habit(self, habit_name: str) -> Dict[str, Any]:
        """
        Record habit completion.
        
        Args:
            habit_name: Name of habit to track
            
        Returns:
            Updated habit info
        """
        for habit in self._habits:
            if habit.habit_name.lower() == habit_name.lower():
                habit.completions += 1
                
                # Update streak
                if habit.last_completed:
                    last = datetime.fromisoformat(habit.last_completed)
                    if (datetime.now() - last).days == 1:
                        habit.streak += 1
                    else:
                        habit.streak = 1
                else:
                    habit.streak = 1
                
                habit.last_completed = datetime.now().isoformat()
                
                self.logger.info(f"[PersonalAnalytics] Tracked habit: {habit_name}")
                
                return {
                    "success": True,
                    "habit": habit.habit_name,
                    "completions": habit.completions,
                    "streak": habit.streak,
                    "message": f"🎉 {habit.habit_name} tracked! Streak: {habit.streak} days"
                }
        
        return {"success": False, "error": f"Habit not found: {habit_name}"}
    
    def get_habit_streak(self, habit_name: str) -> Dict[str, Any]:
        """
        Get streak info for a habit.
        
        Args:
            habit_name: Name of habit
            
        Returns:
            Streak info
        """
        for habit in self._habits:
            if habit.habit_name.lower() == habit_name.lower():
                return {
                    "habit": habit.habit_name,
                    "current_streak": habit.streak,
                    "total_completions": habit.completions,
                    "last_completed": habit.last_completed,
                    "target_per_week": habit.target_per_week,
                    "weekly_progress": self._calculate_weekly_progress(habit)
                }
        
        return {"error": f"Habit not found: {habit_name}"}
    
    def _calculate_weekly_progress(self, habit: HabitRecord) -> Dict:
        """Calculate weekly progress for a habit."""
        week_ago = datetime.now() - timedelta(days=7)
        completions_this_week = 0
        
        # This is simplified - in production would track per-day
        if habit.last_completed:
            if datetime.fromisoformat(habit.last_completed) >= week_ago:
                completions_this_week = min(habit.target_per_week, habit.completions)
        
        return {
            "completed": completions_this_week,
            "target": habit.target_per_week,
            "percentage": round(completions_this_week / habit.target_per_week * 100, 1) if habit.target_per_week > 0 else 0
        }
    
    def get_all_habits(self) -> Dict[str, Any]:
        """
        Get all tracked habits.
        
        Returns:
            List of all habits with stats
        """
        return {
            "count": len(self._habits),
            "habits": [
                {
                    "id": h.id,
                    "name": h.habit_name,
                    "streak": h.streak,
                    "completions": h.completions,
                    "last_completed": h.last_completed,
                    "weekly_progress": self._calculate_weekly_progress(h)
                }
                for h in self._habits
            ]
        }
    
    def delete_habit(self, habit_name: str) -> Dict[str, Any]:
        """
        Delete a habit.
        
        Args:
            habit_name: Name of habit to delete
            
        Returns:
            Result of deletion
        """
        for i, habit in enumerate(self._habits):
            if habit.habit_name.lower() == habit_name.lower():
                self._habits.pop(i)
                self.logger.info(f"[PersonalAnalytics] Deleted habit: {habit_name}")
                return {"success": True, "deleted": habit_name}
        
        return {"success": False, "error": f"Habit not found: {habit_name}"}
    
    # ========== PRODUCTIVITY TOOLS ==========
    
    def get_productivity_score(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate productivity score (0-100).
        
        Args:
            date: Optional date (defaults to today)
            
        Returns:
            Productivity score with breakdown
        """
        summary = self.get_time_summary(date)
        target_focus_minutes = 240  # 4 hours target
        
        # Base score from focus time
        focus_minutes = summary["by_category"].get("development", {}).get("minutes", 0)
        focus_score = min(40, (focus_minutes / target_focus_minutes) * 40)
        
        # Meeting efficiency (less meetings = more score)
        meeting_minutes = summary["by_category"].get("meeting", {}).get("minutes", 0)
        meeting_score = max(0, 20 - (meeting_minutes / 30))  # -1 point per 30 min over 0
        
        # Break taken bonus
        break_minutes = summary["by_category"].get("break", {}).get("minutes", 0)
        break_score = min(20, break_minutes / 5)  # +1 point per 5 min break, max 20
        
        # Task completion bonus
        task_count = summary["entries"]
        task_score = min(20, task_count * 4)  # +4 points per task, max 20
        
        total_score = focus_score + meeting_score + break_score + task_score
        
        # Determine level
        if total_score >= 80:
            level = ProductivityLevel.EXCELLENT
        elif total_score >= 60:
            level = ProductivityLevel.GOOD
        elif total_score >= 40:
            level = ProductivityLevel.AVERAGE
        elif total_score >= 20:
            level = ProductivityLevel.LOW
        else:
            level = ProductivityLevel.POOR
        
        return {
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "score": round(total_score, 1),
            "level": level.value,
            "breakdown": {
                "focus_time": {"score": round(focus_score, 1), "max": 40},
                "meeting_efficiency": {"score": round(meeting_score, 1), "max": 20},
                "breaks": {"score": round(break_score, 1), "max": 20},
                "tasks": {"score": round(task_score, 1), "max": 20}
            },
            "recommendations": self._get_productivity_recommendations(total_score, summary)
        }
    
    def _get_productivity_recommendations(self, score: float, summary: Dict) -> List[str]:
        """Generate productivity recommendations."""
        recommendations = []
        
        if score < 40:
            recommendations.append("💡 Try using Pomodoro technique: 25 min focus, 5 min break")
        
        focus_minutes = summary["by_category"].get("development", {}).get("minutes", 0)
        if focus_minutes < 120:
            recommendations.append("🎯 Aim for at least 2 hours of deep work daily")
        
        meeting_minutes = summary["by_category"].get("meeting", {}).get("minutes", 0)
        if meeting_minutes > 180:
            recommendations.append("📅 Consider batching meetings to free up focus time")
        
        if score >= 80:
            recommendations.append("🚀 Excellent productivity! Keep up the great work!")
        elif score >= 60:
            recommendations.append("👍 Good progress! Try to maintain this level")
        
        return recommendations
    
    def get_peak_hours(self) -> Dict[str, Any]:
        """
        Find your most productive hours.
        
        Returns:
            Analysis of peak productivity hours
        """
        # Analyze time entries to find patterns
        hour_productivity: Dict[int, int] = {h: 0 for h in range(24)}
        
        for entry in self._time_entries:
            if entry.category == TaskCategory.DEVELOPMENT:
                start_hour = datetime.fromisoformat(entry.start_time).hour
                hour_productivity[start_hour] += entry.duration_minutes
        
        # Find top 3 peak hours
        sorted_hours = sorted(hour_productivity.items(), key=lambda x: x[1], reverse=True)
        peak_hours = sorted_hours[:3]
        
        return {
            "peak_hours": [
                {"hour": h, "minutes": mins, "label": self._format_hour(h)}
                for h, mins in peak_hours if mins > 0
            ],
            "least_productive": [
                {"hour": h, "minutes": mins, "label": self._format_hour(h)}
                for h, mins in sorted_hours[-3:] if mins == 0 or mins == min(s[1] for s in sorted_hours)
            ],
            "recommendation": f"Schedule deep work during {self._format_hour(peak_hours[0][0]) if peak_hours else 'your preferred hours'}"
        }
    
    def _format_hour(self, hour: int) -> str:
        """Format hour to readable string."""
        if hour == 0:
            return "12 AM"
        elif hour < 12:
            return f"{hour} AM"
        elif hour == 12:
            return "12 PM"
        else:
            return f"{hour - 12} PM"
    
    # ========== GOAL TRACKING TOOLS ==========
    
    def set_goal(
        self,
        goal_name: str,
        target_value: float,
        unit: str = "hours",
        deadline: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set a productivity goal.
        
        Args:
            goal_name: Name of goal
            target_value: Target value
            unit: Unit of measurement
            deadline: Optional deadline (YYYY-MM-DD)
            
        Returns:
            Goal info
        """
        self._goals[goal_name] = {
            "target": target_value,
            "unit": unit,
            "current": 0,
            "deadline": deadline,
            "created_at": datetime.now().isoformat()
        }
        
        self.logger.info(f"[PersonalAnalytics] Set goal: {goal_name}")
        
        return {
            "name": goal_name,
            "target": target_value,
            "unit": unit,
            "current": 0,
            "deadline": deadline,
            "progress_percentage": 0
        }
    
    def get_goal_progress(self, goal_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get progress on goals.
        
        Args:
            goal_name: Optional specific goal name
            
        Returns:
            Goal progress
        """
        if goal_name:
            if goal_name not in self._goals:
                return {"error": f"Goal not found: {goal_name}"}
            goals = {goal_name: self._goals[goal_name]}
        else:
            goals = self._goals
        
        result = {}
        for name, goal in goals.items():
            progress = min(100, (goal["current"] / goal["target"] * 100) if goal["target"] > 0 else 0)
            result[name] = {
                "target": goal["target"],
                "current": goal["current"],
                "unit": goal["unit"],
                "progress_percentage": round(progress, 1),
                "remaining": max(0, goal["target"] - goal["current"]),
                "deadline": goal.get("deadline"),
                "status": "completed" if progress >= 100 else ("at_risk" if goal.get("deadline") and datetime.now() > datetime.fromisoformat(goal["deadline"]) else "in_progress")
            }
        
        return result
    
    # ========== CATEGORIZATION TOOLS ==========
    
    def categorize_time(self, entry_id: str, category: str) -> Dict[str, Any]:
        """
        Change category of a time entry.
        
        Args:
            entry_id: ID of entry
            category: New category
            
        Returns:
            Updated entry
        """
        for entry in self._time_entries:
            if entry.id == entry_id:
                try:
                    entry.category = TaskCategory(category.lower())
                    self.logger.info(f"[PersonalAnalytics] Recategorized {entry_id} to {category}")
                    return {"success": True, "id": entry_id, "category": entry.category.value}
                except ValueError:
                    return {"success": False, "error": f"Invalid category: {category}"}
        
        return {"success": False, "error": f"Entry not found: {entry_id}"}
    
    def get_category_breakdown(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed category breakdown.
        
        Args:
            date: Optional date
            
        Returns:
            Category breakdown with entries
        """
        summary = self.get_time_summary(date)
        
        # Get entries for date
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        entries = [e for e in self._time_entries if e.start_time.startswith(target_date)]
        
        by_category = {}
        for entry in entries:
            cat = entry.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append({
                "id": entry.id,
                "task": entry.task_name,
                "duration": entry.duration_minutes,
                "notes": entry.notes
            })
        
        return {
            "date": target_date,
            "summary": summary["by_category"],
            "entries": by_category
        }
    
    def get_focus_breakdown(self) -> Dict[str, Any]:
        """
        Get focus vs non-focus time breakdown.
        
        Returns:
            Focus analysis
        """
        total_minutes = sum(e.duration_minutes for e in self._time_entries)
        focus_minutes = sum(
            e.duration_minutes for e in self._time_entries
            if e.category in [TaskCategory.DEVELOPMENT, TaskCategory.LEARNING]
        )
        
        return {
            "total_tracked_minutes": total_minutes,
            "total_tracked_hours": round(total_minutes / 60, 2),
            "focus_minutes": focus_minutes,
            "focus_hours": round(focus_minutes / 60, 2),
            "focus_percentage": round(focus_minutes / total_minutes * 100, 1) if total_minutes > 0 else 0,
            "non_focus_percentage": round((total_minutes - focus_minutes) / total_minutes * 100, 1) if total_minutes > 0 else 0
        }
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive daily summary.
        
        Returns:
            Full daily summary
        """
        productivity = self.get_productivity_score()
        time_summary = self.get_time_summary()
        focus = self.get_focus_breakdown()
        tracking = self.get_current_tracking()
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "productivity_score": productivity["score"],
            "productivity_level": productivity["level"],
            "time_summary": time_summary,
            "focus_breakdown": focus,
            "current_tracking": tracking,
            "quick_stats": {
                "tasks_logged": time_summary["entries"],
                "focus_hours": focus["focus_hours"],
                "total_hours": focus["total_tracked_hours"]
            }
        }


class MockLogger:
    """Mock logger."""
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def get_capability(logger: Optional[ILoggingService] = None) -> PersonalAnalyticsCapability:
    """Factory function."""
    return PersonalAnalyticsCapability(logger=logger)
