"""
Health & Wellness Capability

Provides tools for tracking screen time, break reminders, focus mode, 
and other health-related features.
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


class BreakType(str, Enum):
    """Types of breaks."""
    SHORT = "short"           # 5-10 minutes
    LONG = "long"             # 15-30 minutes
    EYE_REST = "eye_rest"     # 20-20-20 rule (every 20 min, look 20ft away for 20 sec)
    POSTURE = "posture"        # Posture check
    HYDRATION = "hydration"    # Drink water
    MOVEMENT = "movement"      # Stretch/walk


class FocusMode(str, Enum):
    """Focus mode levels."""
    OFF = "off"
    POMODORO = "pomodoro"     # 25 min work, 5 min break
    DEEP_WORK = "deep_work"   # 90 min work, 20 min break
    ZEN = "zen"               # No interruptions


@dataclass
class ScreenTimeEntry:
    """A screen time tracking entry."""
    app_name: str
    window_title: str
    start_time: str
    end_time: Optional[str]
    duration_seconds: int
    category: str = "unknown"


@dataclass
class BreakReminder:
    """A scheduled break reminder."""
    id: str
    break_type: BreakType
    scheduled_at: str
    message: str
    completed: bool = False
    skipped: bool = False


@dataclass
class FocusSession:
    """A focus session."""
    id: str
    mode: FocusMode
    started_at: str
    ended_at: Optional[str]
    work_duration_minutes: int
    break_duration_minutes: int
    completed_sessions: int
    interrupted: bool = False


class HealthCapability:
    """
    Health & Wellness capability for CHITTI.
    
    Tools:
    - get_screen_time: Get today's screen time by app
    - set_break_reminder: Schedule a break reminder
    - list_break_reminders: List all break reminders
    - cancel_break_reminder: Cancel a break reminder
    - enable_focus_mode: Start a focus session
    - disable_focus_mode: End focus session
    - get_focus_status: Get current focus status
    - snooze_break: Snooze current break
    - skip_break: Skip current break
    - get_health_summary: Get overall health summary
    - set_pomodoro: Set Pomodoro timer
    - get_posture_reminder: Check posture
    """
    
    def __init__(self, logger: Optional[ILoggingService] = None):
        self.logger = logger or MockLogger()
        self._state = ServiceState.STOPPED
        self._is_healthy = True
        
        # Data storage
        self._screen_time_entries: List[ScreenTimeEntry] = []
        self._break_reminders: List[BreakReminder] = []
        self._focus_sessions: List[FocusSession] = []
        self._current_focus: Optional[FocusSession] = None
        self._current_break: Optional[BreakReminder] = None
        
        # Settings
        self._pomodoro_work = 25  # minutes
        self._pomodoro_break = 5  # minutes
        self._long_break = 15     # minutes
        self._sessions_until_long = 4
        
        self.logger.info("[HealthCapability] Initialized")
    
    @property
    def name(self) -> str:
        return "HealthCapability"
    
    @property
    def state(self) -> ServiceState:
        return self._state
    
    def initialize(self) -> None:
        """Initialize the capability."""
        self._state = ServiceState.RUNNING
        self._is_healthy = True
        self.logger.info("[HealthCapability] Started")
    
    def shutdown(self) -> None:
        """Shutdown the capability."""
        self._state = ServiceState.STOPPED
        self.logger.info("[HealthCapability] Stopped")
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy" if self._is_healthy else "unhealthy",
            "focus_active": self._current_focus is not None,
            "current_break": self._current_break.break_type if self._current_break else None
        }
    
    def discover_tools(self) -> List[str]:
        """Return list of available tools."""
        return [
            "get_screen_time",
            "get_weekly_screen_time",
            "set_break_reminder",
            "list_break_reminders",
            "cancel_break_reminder",
            "snooze_break",
            "skip_break",
            "enable_focus_mode",
            "disable_focus_mode",
            "get_focus_status",
            "get_health_summary",
            "set_pomodoro_settings",
            "get_posture_reminder",
            "enable_eye_rest",
            "get_hydration_reminder"
        ]
    
    # ========== SCREEN TIME TOOLS ==========
    
    def get_screen_time(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get today's screen time breakdown by application.
        
        Args:
            date: Optional date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Screen time summary by app
        """
        today = date or datetime.now().strftime("%Y-%m-%d")
        
        # Filter entries for today
        today_entries = [
            e for e in self._screen_time_entries
            if e.start_time.startswith(today)
        ]
        
        # Aggregate by app
        app_times: Dict[str, int] = {}
        for entry in today_entries:
            if entry.app_name not in app_times:
                app_times[entry.app_name] = 0
            app_times[entry.app_name] += entry.duration_seconds
        
        total_seconds = sum(app_times.values())
        total_hours = total_seconds / 3600
        
        return {
            "date": today,
            "total_hours": round(total_hours, 2),
            "total_seconds": total_seconds,
            "by_app": {
                app: {
                    "seconds": secs,
                    "hours": round(secs / 3600, 2),
                    "percentage": round(secs / total_seconds * 100, 1) if total_seconds > 0 else 0
                }
                for app, secs in app_times.items()
            },
            "entry_count": len(today_entries)
        }
    
    def get_weekly_screen_time(self) -> Dict[str, Any]:
        """
        Get screen time summary for the past 7 days.
        
        Returns:
            Weekly screen time summary
        """
        today = datetime.now()
        week_data = []
        
        for i in range(7):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            daily = self.get_screen_time(date)
            week_data.append({
                "date": date,
                "total_hours": daily["total_hours"]
            })
        
        total_week_seconds = sum(
            entry.duration_seconds 
            for entry in self._screen_time_entries
            if (datetime.now() - datetime.fromisoformat(entry.start_time)).days < 7
        )
        
        return {
            "days": week_data,
            "total_week_hours": round(total_week_seconds / 3600, 2),
            "daily_average_hours": round((total_week_seconds / 3600) / 7, 2),
            "goal_hours_per_day": 6,
            "goal_met": (total_week_seconds / 3600 / 7) <= 6
        }
    
    # ========== BREAK REMINDER TOOLS ==========
    
    def set_break_reminder(
        self,
        break_type: str,
        minutes: int = 30,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a break reminder.
        
        Args:
            break_type: Type of break (short, long, eye_rest, posture, hydration, movement)
            minutes: Minutes until break
            message: Custom reminder message
            
        Returns:
            Created reminder info
        """
        try:
            btype = BreakType(break_type.lower())
        except ValueError:
            return {"error": f"Invalid break type: {break_type}"}
        
        reminder_id = f"break_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        scheduled_at = datetime.now() + timedelta(minutes=minutes)
        
        default_messages = {
            BreakType.SHORT: "Time for a short break! Stand up and stretch.",
            BreakType.LONG: "Long break time! Take a walk or grab a coffee.",
            BreakType.EYE_REST: "Eye rest: Look at something 20 feet away for 20 seconds.",
            BreakType.POSTURE: "Posture check: Sit up straight, relax your shoulders.",
            BreakType.HYDRATION: "Hydration reminder: Drink some water!",
            BreakType.MOVEMENT: "Movement time: Do some stretches or walk around."
        }
        
        reminder = BreakReminder(
            id=reminder_id,
            break_type=btype,
            scheduled_at=scheduled_at.isoformat(),
            message=message or default_messages.get(btype, "Time for a break!"),
            completed=False,
            skipped=False
        )
        
        self._break_reminders.append(reminder)
        self.logger.info(f"[HealthCapability] Break reminder set: {reminder_id}")
        
        return {
            "id": reminder_id,
            "break_type": btype.value,
            "scheduled_at": reminder.scheduled_at,
            "message": reminder.message,
            "minutes_until": minutes
        }
    
    def list_break_reminders(self, active_only: bool = True) -> Dict[str, Any]:
        """
        List all break reminders.
        
        Args:
            active_only: Only show pending reminders
            
        Returns:
            List of reminders
        """
        reminders = self._break_reminders
        
        if active_only:
            reminders = [r for r in reminders if not r.completed and not r.skipped]
        
        return {
            "count": len(reminders),
            "reminders": [
                {
                    "id": r.id,
                    "break_type": r.break_type.value,
                    "scheduled_at": r.scheduled_at,
                    "message": r.message,
                    "status": "completed" if r.completed else ("skipped" if r.skipped else "pending")
                }
                for r in reminders
            ]
        }
    
    def cancel_break_reminder(self, reminder_id: str) -> Dict[str, Any]:
        """
        Cancel a break reminder.
        
        Args:
            reminder_id: ID of reminder to cancel
            
        Returns:
            Result of cancellation
        """
        for reminder in self._break_reminders:
            if reminder.id == reminder_id:
                reminder.skipped = True
                self.logger.info(f"[HealthCapability] Break reminder cancelled: {reminder_id}")
                return {"success": True, "id": reminder_id}
        
        return {"success": False, "error": f"Reminder not found: {reminder_id}"}
    
    def snooze_break(self, reminder_id: str, minutes: int = 5) -> Dict[str, Any]:
        """
        Snooze a break reminder.
        
        Args:
            reminder_id: ID of reminder to snooze
            minutes: Minutes to snooze
            
        Returns:
            Updated reminder info
        """
        for reminder in self._break_reminders:
            if reminder.id == reminder_id:
                new_time = datetime.fromisoformat(reminder.scheduled_at) + timedelta(minutes=minutes)
                reminder.scheduled_at = new_time.isoformat()
                self.logger.info(f"[HealthCapability] Break reminder snoozed: {reminder_id} +{minutes}min")
                return {
                    "success": True,
                    "id": reminder_id,
                    "new_time": reminder.scheduled_at
                }
        
        return {"success": False, "error": f"Reminder not found: {reminder_id}"}
    
    def skip_break(self, reminder_id: str) -> Dict[str, Any]:
        """
        Skip a break reminder.
        
        Args:
            reminder_id: ID of reminder to skip
            
        Returns:
            Result of skip
        """
        return self.cancel_break_reminder(reminder_id)
    
    # ========== FOCUS MODE TOOLS ==========
    
    def enable_focus_mode(
        self,
        mode: str = "pomodoro",
        duration_minutes: int = 25
    ) -> Dict[str, Any]:
        """
        Enable focus mode.
        
        Args:
            mode: Focus mode (pomodoro, deep_work, zen)
            duration_minutes: Duration for the session
            
        Returns:
            Focus session info
        """
        try:
            fmode = FocusMode(mode.lower())
        except ValueError:
            return {"error": f"Invalid focus mode: {mode}"}
        
        session_id = f"focus_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        work_duration = duration_minutes
        if fmode == FocusMode.POMODORO:
            break_duration = self._pomodoro_break
        elif fmode == FocusMode.DEEP_WORK:
            break_duration = self._long_break
        else:
            break_duration = 0
        
        session = FocusSession(
            id=session_id,
            mode=fmode,
            started_at=datetime.now().isoformat(),
            ended_at=None,
            work_duration_minutes=work_duration,
            break_duration_minutes=break_duration,
            completed_sessions=0,
            interrupted=False
        )
        
        self._current_focus = session
        self._focus_sessions.append(session)
        self.logger.info(f"[HealthCapability] Focus mode enabled: {session_id}")
        
        return {
            "id": session_id,
            "mode": fmode.value,
            "started_at": session.started_at,
            "work_duration_minutes": work_duration,
            "break_duration_minutes": break_duration,
            "end_time": (datetime.now() + timedelta(minutes=work_duration)).isoformat()
        }
    
    def disable_focus_mode(self, interrupted: bool = False) -> Dict[str, Any]:
        """
        Disable focus mode.
        
        Args:
            interrupted: Whether session was interrupted
            
        Returns:
            Session summary
        """
        if not self._current_focus:
            return {"error": "No active focus session"}
        
        session = self._current_focus
        session.ended_at = datetime.now().isoformat()
        session.interrupted = interrupted
        
        result = {
            "id": session.id,
            "mode": session.mode.value,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "completed_sessions": session.completed_sessions,
            "was_interrupted": interrupted
        }
        
        self._current_focus = None
        self.logger.info(f"[HealthCapability] Focus mode disabled: {session.id}")
        
        return result
    
    def get_focus_status(self) -> Dict[str, Any]:
        """
        Get current focus mode status.
        
        Returns:
            Current focus status
        """
        if not self._current_focus:
            return {
                "active": False,
                "mode": None
            }
        
        session = self._current_focus
        started = datetime.fromisoformat(session.started_at)
        elapsed = (datetime.now() - started).total_seconds() / 60
        remaining = max(0, session.work_duration_minutes - elapsed)
        
        return {
            "active": True,
            "id": session.id,
            "mode": session.mode.value,
            "started_at": session.started_at,
            "elapsed_minutes": round(elapsed, 1),
            "remaining_minutes": round(remaining, 1),
            "completed_sessions": session.completed_sessions,
            "next_break_in": round(remaining, 1) if remaining > 0 else 0
        }
    
    # ========== HEALTH SUMMARY TOOLS ==========
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get overall health and wellness summary.
        
        Returns:
            Health summary including screen time, breaks, focus
        """
        screen_time = self.get_screen_time()
        active_breaks = self.list_break_reminders(active_only=True)
        focus_status = self.get_focus_status()
        weekly = self.get_weekly_screen_time()
        
        # Calculate health score (0-100)
        health_score = 100
        
        # Deduct for excessive screen time (>6 hours)
        if screen_time["total_hours"] > 6:
            health_score -= int((screen_time["total_hours"] - 6) * 10)
        
        # Deduct for missed breaks
        missed_breaks = sum(
            1 for r in self._break_reminders 
            if r.scheduled_at < datetime.now().isoformat() 
            and not r.completed 
            and not r.skipped
        )
        health_score -= missed_breaks * 5
        
        # Add points for completed breaks
        completed_breaks = sum(1 for r in self._break_reminders if r.completed)
        health_score += min(completed_breaks * 2, 20)
        
        health_score = max(0, min(100, health_score))
        
        return {
            "score": health_score,
            "screen_time": {
                "today_hours": screen_time["total_hours"],
                "weekly_hours": weekly["total_week_hours"],
                "daily_average": weekly["daily_average_hours"],
                "goal_met": weekly["goal_met"]
            },
            "breaks": {
                "active_reminders": active_breaks["count"],
                "completed_today": completed_breaks
            },
            "focus": {
                "mode_active": focus_status["active"],
                "current_mode": focus_status.get("mode")
            },
            "recommendations": self._generate_recommendations(health_score, screen_time)
        }
    
    def _generate_recommendations(self, score: int, screen_time: Dict) -> List[str]:
        """Generate health recommendations based on data."""
        recommendations = []
        
        if screen_time["total_hours"] > 8:
            recommendations.append("⚠️ You've been on screens for over 8 hours today. Consider taking a long break.")
        elif screen_time["total_hours"] > 6:
            recommendations.append("💡 Consider taking more breaks - you're approaching healthy screen time limits.")
        
        if score < 50:
            recommendations.append("🎯 Your health score is low. Enable focus mode to improve productivity.")
        
        if not self._current_focus:
            recommendations.append("🍅 Try a Pomodoro session: 25 min work, 5 min break.")
        
        pending_breaks = [
            r for r in self._break_reminders 
            if r.scheduled_at < datetime.now().isoformat() 
            and not r.completed 
            and not r.skipped
        ]
        if pending_breaks:
            recommendations.append(f"⏰ You have {len(pending_breaks)} overdue break(s).")
        
        if not recommendations:
            recommendations.append("✅ You're doing great! Keep up the healthy habits.")
        
        return recommendations
    
    # ========== POMODORO TOOLS ==========
    
    def set_pomodoro_settings(
        self,
        work_minutes: int = 25,
        break_minutes: int = 5,
        long_break_minutes: int = 15,
        sessions_until_long: int = 4
    ) -> Dict[str, Any]:
        """
        Configure Pomodoro timer settings.
        
        Args:
            work_minutes: Work duration in minutes
            break_minutes: Short break duration
            long_break_minutes: Long break duration
            sessions_until_long: Sessions before long break
            
        Returns:
            Updated settings
        """
        self._pomodoro_work = max(1, min(60, work_minutes))
        self._pomodoro_break = max(1, min(30, break_minutes))
        self._long_break = max(5, min(60, long_break_minutes))
        self._sessions_until_long = max(2, min(10, sessions_until_long))
        
        self.logger.info(f"[HealthCapability] Pomodoro settings updated")
        
        return {
            "work_minutes": self._pomodoro_work,
            "break_minutes": self._pomodoro_break,
            "long_break_minutes": self._long_break,
            "sessions_until_long": self._sessions_until_long
        }
    
    # ========== EYE REST TOOLS ==========
    
    def enable_eye_rest(self, interval_minutes: int = 20) -> Dict[str, Any]:
        """
        Enable 20-20-20 eye rest rule.
        Every X minutes, remind user to look at something 20 feet away.
        
        Args:
            interval_minutes: Minutes between reminders
            
        Returns:
            Eye rest settings
        """
        reminder = self.set_break_reminder(
            break_type="eye_rest",
            minutes=interval_minutes,
            message="👀 20-20-20 Rule: Look at something 20 feet away for 20 seconds!"
        )
        
        return {
            "enabled": True,
            "interval_minutes": interval_minutes,
            "reminder": reminder
        }
    
    # ========== HYDRATION TOOLS ==========
    
    def get_hydration_reminder(self) -> Dict[str, Any]:
        """
        Get hydration reminder based on screen time.
        
        Returns:
            Hydration recommendation
        """
        screen_time = self.get_screen_time()
        hours = screen_time["total_hours"]
        
        # Rough estimate: 1 glass per hour of screen time, max 8
        glasses = min(8, max(1, int(hours)))
        
        return {
            "screen_time_hours": hours,
            "recommended_glasses": glasses,
            "message": f"💧 You've been on screens for {hours:.1f} hours. Drink about {glasses} glass(es) of water!",
            "tip": "Staying hydrated helps maintain focus and reduces eye strain."
        }
    
    # ========== POSTURE TOOLS ==========
    
    def get_posture_reminder(self) -> Dict[str, Any]:
        """
        Get posture check reminder.
        
        Returns:
            Posture tips and reminder
        """
        return {
            "check": True,
            "reminder": "🧘 Posture check:",
            "checks": [
                "✓ Back straight against chair",
                "✓ Shoulders relaxed, not hunched",
                "✓ Screen at eye level",
                "✓ Arms at 90 degrees",
                "✓ Feet flat on floor"
            ],
            "message": "Take a moment to adjust your posture if needed."
        }


class MockLogger:
    """Mock logger for when no logger is provided."""
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def get_capability(logger: Optional[ILoggingService] = None) -> HealthCapability:
    """Factory function to create capability."""
    return HealthCapability(logger=logger)
