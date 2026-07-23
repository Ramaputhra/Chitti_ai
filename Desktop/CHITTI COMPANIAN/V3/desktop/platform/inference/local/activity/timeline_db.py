import sqlite3
import os
from typing import List, Optional
from desktop.platform.shared.models.activity import ActivitySession
from desktop.services.logging.logging_service import ILoggingService

class TimelineDatabase:
    """
    Dedicated SQLite database for high-frequency timeline data.
    Keeps historical activity facts isolated from semantic/episodic memory.
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
                    session_id TEXT PRIMARY KEY,
                    app_name TEXT,
                    window_title TEXT,
                    workspace TEXT,
                    activity_type TEXT,
                    start_time REAL,
                    end_time REAL,
                    duration REAL,
                    project_id TEXT,
                    goal_id TEXT,
                    interrupted_by TEXT,
                    switch_reason TEXT
                )
            ''')
            # Indexes for fast querying
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_start_time ON desktop_activities(start_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_name ON desktop_activities(app_name)')
            conn.commit()

    def log_session(self, session: ActivitySession):
        """
        Inserts or updates an activity session in the timeline database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO desktop_activities (
                    session_id, app_name, window_title, workspace, activity_type,
                    start_time, end_time, duration, project_id, goal_id,
                    interrupted_by, switch_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    end_time=excluded.end_time,
                    duration=excluded.duration,
                    window_title=excluded.window_title,
                    project_id=excluded.project_id,
                    goal_id=excluded.goal_id,
                    interrupted_by=excluded.interrupted_by,
                    switch_reason=excluded.switch_reason
            ''', (
                session.session_id, session.app_name, session.window_title, session.workspace, session.activity_type,
                session.start_time, session.end_time, session.duration, session.project_id, session.goal_id,
                session.interrupted_by, session.switch_reason
            ))
            conn.commit()

    def get_recent_sessions(self, limit: int = 5) -> List[ActivitySession]:
        """
        Retrieves the most recent sessions ordered by start_time descending.
        """
        sessions = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_id, app_name, window_title, workspace, activity_type,
                       start_time, end_time, duration, project_id, goal_id,
                       interrupted_by, switch_reason
                FROM desktop_activities
                ORDER BY start_time DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            for row in rows:
                session = ActivitySession(
                    session_id=row[0],
                    app_name=row[1],
                    window_title=row[2],
                    workspace=row[3],
                    activity_type=row[4],
                    start_time=row[5],
                    end_time=row[6],
                    project_id=row[8],
                    goal_id=row[9],
                    interrupted_by=row[10],
                    switch_reason=row[11]
                )
                sessions.append(session)
        return sessions
