import sqlite3
import os
from typing import List, Optional
from desktop.platform.shared.models.activity import (
    ActivitySession, ActivitySessionState, ActivitySource,
    ActivityCategory, ActivityEndedReason
)
from desktop.services.logging.logging_service import ILoggingService

class ActivityStore:
    """
    Dedicated SQLite repository for high-frequency activity data.
    Keeps historical activity facts isolated from semantic/episodic memory.
    Strictly follows repository pattern; exposes no SQL details.
    """
    def __init__(self, db_path: str, logger: ILoggingService):
        self.db_path = db_path
        self.logger = logger
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS desktop_activities (
                    activity_id TEXT PRIMARY KEY,
                    state TEXT,
                    source TEXT,
                    confidence REAL,
                    app_name TEXT,
                    window_title TEXT,
                    workspace TEXT,
                    category TEXT,
                    start_time REAL,
                    end_time REAL,
                    duration REAL,
                    ended_reason TEXT,
                    project_id TEXT,
                    goal_id TEXT,
                    interrupted_by TEXT,
                    switch_reason TEXT,
                    workspace_key TEXT
                )
            ''')
            # Indexes for fast querying
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_start_time ON desktop_activities(start_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_workspace_key ON desktop_activities(workspace_key)')
            conn.commit()

    def save_session(self, session: ActivitySession):
        """
        Inserts or updates an activity session in the activity store.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO desktop_activities (
                    activity_id, state, source, confidence, app_name, window_title, 
                    workspace, category, start_time, end_time, duration, ended_reason,
                    project_id, goal_id, interrupted_by, switch_reason, workspace_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(activity_id) DO UPDATE SET
                    state=excluded.state,
                    end_time=excluded.end_time,
                    duration=excluded.duration,
                    ended_reason=excluded.ended_reason,
                    window_title=excluded.window_title,
                    project_id=excluded.project_id,
                    goal_id=excluded.goal_id,
                    interrupted_by=excluded.interrupted_by,
                    switch_reason=excluded.switch_reason
            ''', (
                session.activity_id, session.state.value, session.source.value, session.confidence,
                session.app_name, session.window_title, session.workspace, session.category.value,
                session.start_time, session.end_time, session.duration,
                session.ended_reason.value if session.ended_reason else None,
                session.project_id, session.goal_id, session.interrupted_by,
                session.switch_reason, session.workspace_key
            ))
            conn.commit()

    def get_session(self, activity_id: str) -> Optional[ActivitySession]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM desktop_activities WHERE activity_id = ?', (activity_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_session(row)

    def get_recent_sessions(self, limit: int = 5) -> List[ActivitySession]:
        """
        Retrieves the most recent sessions ordered by start_time descending.
        """
        sessions = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM desktop_activities ORDER BY start_time DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            for row in rows:
                sessions.append(self._row_to_session(row))
        return sessions

    def find_between(self, start_time: float, end_time: float) -> List[ActivitySession]:
        sessions = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM desktop_activities 
                WHERE start_time >= ? AND start_time <= ?
                ORDER BY start_time ASC
            ''', (start_time, end_time))
            rows = cursor.fetchall()
            for row in rows:
                sessions.append(self._row_to_session(row))
        return sessions

    def find_by_workspace(self, workspace_key: str) -> List[ActivitySession]:
        sessions = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM desktop_activities 
                WHERE workspace_key = ?
                ORDER BY start_time DESC
            ''', (workspace_key,))
            rows = cursor.fetchall()
            for row in rows:
                sessions.append(self._row_to_session(row))
        return sessions
        
    def _row_to_session(self, row) -> ActivitySession:
        return ActivitySession(
            activity_id=row[0],
            state=ActivitySessionState(row[1]),
            source=ActivitySource(row[2]),
            confidence=row[3],
            app_name=row[4],
            window_title=row[5],
            workspace=row[6],
            category=ActivityCategory(row[7]),
            start_time=row[8],
            end_time=row[9],
            ended_reason=ActivityEndedReason(row[11]) if row[11] else None,
            project_id=row[12],
            goal_id=row[13],
            interrupted_by=row[14],
            switch_reason=row[15],
            workspace_key=row[16]
        )
