import sqlite3
import os
from typing import List, Optional
from desktop.platform.shared.models.goal import (
    Project, Goal, WorkspaceMapping,
    ProjectStatus, GoalStatus, AssignmentSource
)
from desktop.services.logging.logging_service import ILoggingService

class GoalStore:
    """
    Dedicated SQLite repository for Goal and Project persistence (long-term working memory).
    Separate from ActivityStore (historical timeline) and MemoryStore (semantic memory).
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
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    status TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    goal_id TEXT PRIMARY KEY,
                    project_id TEXT,
                    name TEXT,
                    description TEXT,
                    status TEXT,
                    estimated_minutes REAL,
                    tracked_minutes REAL,
                    completion_percentage REAL,
                    last_activity REAL,
                    created_at REAL,
                    updated_at REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workspace_mappings (
                    mapping_id TEXT PRIMARY KEY,
                    workspace_key TEXT,
                    target_id TEXT,
                    target_type TEXT,
                    confidence REAL,
                    assignment_source TEXT,
                    created_at REAL
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_goal_project ON goals(project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_mapping_workspace ON workspace_mappings(workspace_key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_mapping_target ON workspace_mappings(target_id)')
            conn.commit()

    def save_project(self, project: Project):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO projects (project_id, name, description, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    name=excluded.name,
                    description=excluded.description,
                    status=excluded.status,
                    updated_at=excluded.updated_at
            ''', (
                project.project_id, project.name, project.description,
                project.status.value, project.created_at, project.updated_at
            ))
            conn.commit()

    def get_project(self, project_id: str) -> Optional[Project]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM projects WHERE project_id = ?', (project_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Project(
                project_id=row[0],
                name=row[1],
                description=row[2],
                status=ProjectStatus(row[3]),
                created_at=row[4],
                updated_at=row[5]
            )

    def save_goal(self, goal: Goal):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO goals (
                    goal_id, project_id, name, description, status,
                    estimated_minutes, tracked_minutes, completion_percentage,
                    last_activity, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(goal_id) DO UPDATE SET
                    project_id=excluded.project_id,
                    name=excluded.name,
                    description=excluded.description,
                    status=excluded.status,
                    estimated_minutes=excluded.estimated_minutes,
                    tracked_minutes=excluded.tracked_minutes,
                    completion_percentage=excluded.completion_percentage,
                    last_activity=excluded.last_activity,
                    updated_at=excluded.updated_at
            ''', (
                goal.goal_id, goal.project_id, goal.name, goal.description,
                goal.status.value, goal.estimated_minutes, goal.tracked_minutes,
                goal.completion_percentage, goal.last_activity,
                goal.created_at, goal.updated_at
            ))
            conn.commit()

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM goals WHERE goal_id = ?', (goal_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Goal(
                goal_id=row[0],
                project_id=row[1],
                name=row[2],
                description=row[3],
                status=GoalStatus(row[4]),
                estimated_minutes=row[5],
                tracked_minutes=row[6],
                completion_percentage=row[7],
                last_activity=row[8],
                created_at=row[9],
                updated_at=row[10]
            )

    def add_mapping(self, mapping: WorkspaceMapping):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workspace_mappings (
                    mapping_id, workspace_key, target_id, target_type,
                    confidence, assignment_source, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(mapping_id) DO UPDATE SET
                    confidence=excluded.confidence,
                    assignment_source=excluded.assignment_source
            ''', (
                mapping.mapping_id, mapping.workspace_key, mapping.target_id,
                mapping.target_type, mapping.confidence,
                mapping.assignment_source.value, mapping.created_at
            ))
            conn.commit()

    def get_mappings_for_workspace(self, workspace_key: str) -> List[WorkspaceMapping]:
        mappings = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM workspace_mappings WHERE workspace_key = ?', (workspace_key,))
            rows = cursor.fetchall()
            for row in rows:
                mappings.append(WorkspaceMapping(
                    mapping_id=row[0],
                    workspace_key=row[1],
                    target_id=row[2],
                    target_type=row[3],
                    confidence=row[4],
                    assignment_source=AssignmentSource(row[5]),
                    created_at=row[6]
                ))
        return mappings
